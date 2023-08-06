-- An interface to the game Super Mario Bros through the emulator FCEUX using
-- Unix pipes as a communication medium

-- MARK: Environment helpers
-- Lua sucks and doesn't have a lot of primitive built in functions. This is
-- a short list of them needed here

-- Split the string into a table based on a delimiting value
function split(self, delimiter)
    local results = {}
    local start = 1
    local split_start, split_end    = string.find(self, delimiter, start)
    while split_start do
        table.insert(results, string.sub(self, start, split_start - 1))
        start = split_end + 1
        split_start, split_end = string.find(self, delimiter, start)
    end
    table.insert(results, string.sub(self, start))
    return results
end



-- MARK: Memory Map
-- The following methods provide an interface to the runtime memory map of the
-- NES game. They both return data like scores and lives, and provide hacks
-- for skipping cut-scenes and speeding up animations.

-- a local copy of the current x position of Mario
local x_pos = 0
-- a local copy of the value of the in game clock
local time = 0

-- Read a range of bytes and return a number
function readbyterange(address, length)
    local return_value = 0
    for offset = 0,length-1 do
        return_value = return_value * 10
        return_value = return_value + memory.readbyte(address + offset)
    end
    return return_value
end

-- Return the current level (0-indexed) (0 to 31)
function get_level()
    -- Read the world 0x075f as the base and add the level. there are 4 levels
    -- per world
    return memory.readbyte(0x075f) * 4 + memory.readbyte(0x075c)
end

-- Return the current world number (1 to 8)
function get_world_number()
    return memory.readbyte(0x075f) + 1
end

-- Return the current level number (1 to 4)
function get_level_number()
    return memory.readbyte(0x075c) + 1
end

-- Return the current area number (1 to 5)
function get_area_number()
    return memory.readbyte(0x0760) + 1
end

-- Return the current player score (0 to 999990)
function get_score()
    return tonumber(readbyterange(0x07de, 6))
end

-- Return the time left (0 to 999)
function get_time()
    return tonumber(readbyterange(0x07f8, 3))
end

-- Return the number of coins collected (0 to 99)
function get_coins()
    return tonumber(readbyterange(0x07ed, 2))
end

-- Return the number of remaining lives
function get_life()
    return memory.readbyte(0x075a)
end

-- Return the current horizontal position
function get_x_position()
    -- add the current page 0x6d to the current x
    return memory.readbyte(0x6d) * 0x100 + memory.readbyte(0x86)
end

-- Return the number of pixels from the left of the screen
function get_left_x_position()
    -- subtract the left x position 0x071c from the current x 0x86
    return (memory.readbyte(0x86) - memory.readbyte(0x071c)) % 256
end

-- Return the current vertical position
function get_y_position()
    return memory.readbyte(0x03b8)
end

-- Return the current y viewport
-- 1 = in visible viewport
-- 0 = above viewport
-- > 1 below viewport (i.e. dead, falling down a hole)
-- up to 5 indicates falling into a hole
function get_y_viewport()
    return memory.readbyte(0x00b5)
end

-- Return the player status
-- 0 --> small Mario
-- 1 --> tall Mario
-- 2+ -> fireball Mario
function get_player_status()
    return memory.readbyte(0x0756)
end

-- Return the current player state:
-- 0x00 -> Leftmost of screen
-- 0x01 -> Climbing vine
-- 0x02 -> Entering reversed-L pipe
-- 0x03 -> Going down a pipe
-- 0x04 -> Auto-walk
-- 0x05 -> Auto-walk
-- 0x06 -> Dead
-- 0x07 -> Entering area
-- 0x08 -> Normal
-- 0x09 -> Cannot move
-- 0x0B -> Dying
-- 0x0C -> Palette cycling, can't move
function get_player_state()
    return memory.readbyte(0x000e)
end

-- Return a boolean determining if Mario is in the dying animation
function is_dying()
    return get_player_state() == 0x0b or get_y_viewport() > 1
end

-- Return a boolean determining if Mario is in the dead state
function is_dead()
    return get_player_state() == 0x06
end

-- Return 1 if the game has ended or a 0 if it has not
function is_game_over()
    return get_life() == 0xff
end

-- a table of player_state values indicating that Mario is occupied
occupied = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x07}
-- Return boolean determining if Mario is occupied by in-game garbage
function is_occupied()
    local is_occupied = false
    local player_state = get_player_state()
    -- iterate over the values in the occupied table
    for i, state_code in ipairs(occupied) do
        is_occupied = is_occupied or player_state == state_code
    end
    return is_occupied
end

-- Hacks

-- Force the pre-level timer to 0 to skip the unnecessary frames during a
-- death transition
function runout_prelevel_timer()
    memory.writebyte(0x07A0, 0)
end

-- Skip the change area animations by checking for the timers sentinel values
-- and running them out
function skip_change_area()
    local change_area_timer = memory.readbyte(0x06DE)
    if change_area_timer > 1 and change_area_timer < 255 then
        memory.writebyte(0x06DE, 1)
        emu.frameadvance()
    end
end

-- Skip occupied states by running out a timer and skipping frames
function skip_occupied_states()
    while is_occupied() do
        runout_prelevel_timer()
        emu.frameadvance()
    end
end

-- Write the value to memory indicating that Mario has died to skip a dying
-- animation.
function kill_mario()
    -- if there is a specific level specified, ignore the notion of lives
    if target_world ~= nil and target_level ~= nil then
        memory.writebyte(0x075a, 0)
    end
    -- force Mario's state to dead
    memory.writebyte(0x000e, 0x06)
end

-- Rewards

-- Return the reward for moving forward on the x-axis
function get_x_reward()
    local next_x_pos = get_x_position()
    local _reward = next_x_pos - x_pos
    x_pos = next_x_pos
    -- resolve an issue where after death the x position resets. The x delta
    -- is typically has at most magnitude of 3, 5 is a safe bound
    if _reward < -5 or _reward > 5 then
        return 0
    end

    return _reward
end

-- Return the penalty for staying alive. i.e. the reward stream designed
-- to convince the agent to be fast
function get_time_penalty()
    local next_time = get_time()
    local _reward = next_time - time
    time = next_time
    -- time can only decrease, a positive reward results from a reset and
    -- should default to 0 reward
    if _reward > 0 then
        return 0
    end

    return _reward
end

-- Return a penalty for
function get_death_penalty()
    if is_dying() or is_dead() then
        return -15
    end
    return 0
end

-- Return the cumulative reward at the current state
function get_reward()
    return get_x_reward() + get_time_penalty() + get_death_penalty()
end





-- memory addresses for the world, level, and area
addr_world = 0x075f;
addr_level = 0x075c;
addr_area = 0x0760;
-- get the target world and level from environment variables
target_world = tonumber(os.getenv("target_world"))
target_level = tonumber(os.getenv("target_level"))
target_area = target_level
lost_levels = tonumber(os.getenv("lost_levels"))
-- setup the target world and level if specified
if target_world ~= nil and target_level ~= nil then
    -- setup the target area depending on whether this is SMB 1 or 2
    if lost_levels == 1 then
        -- setup the target area depending on the target world and level
        if (target_world == 1) or (target_world == 3) then
            if (target_level >= 2) then
                target_area = target_area + 1;
            end;
        elseif (target_world >= 5) then
            -- TODO: figure out why all worlds greater than 5 seem to fail.
            -- >=6 causes a change for
            target_area = target_area + 1;
        end;
    else
        -- setup the target area depending on the target world and level
        if (target_world == 1) or (target_world == 2) or (target_world == 4) or (target_world == 7) then
            if (target_level >= 2) then
                target_area = target_area + 1;
            end;
        end;
    end;
    -- Respond to the memory address for the world being set
    function hook_set_world()
        if (get_world_number() ~= target_world) then
            memory.writebyte(addr_world, (target_world - 1));
            memory.writebyte(addr_level, (target_level - 1));
            memory.writebyte(addr_area, (target_area - 1));
        end;
    end;
    memory.registerwrite(addr_world, hook_set_world);

    -- Respond to the memory address for the level being set
    function hook_set_level()
        if (get_level_number() ~= target_level) then
            memory.writebyte(addr_world, (target_world - 1));
            memory.writebyte(addr_level, (target_level - 1));
            memory.writebyte(addr_area, (target_area - 1));
        end;
    end;
    memory.registerwrite(addr_level, hook_set_level);

    -- Respond to the memory address for the area being set
    function hook_set_area()
        if (get_area_number() ~= target_area) then
            memory.writebyte(addr_world, (target_world - 1));
            memory.writebyte(addr_level, (target_level - 1));
            memory.writebyte(addr_area, (target_area - 1));
        end;
    end;
    memory.registerwrite(addr_area, hook_set_area);

end;




-- MARK: Emulator
-- The following methods provide an interface to the machinery of the emulator
-- for storing resetting the game, storing screens, stepping forward, etc.
-- The communication logic using pipes lives here as well

-- A separator for the outbound communication protocol. ASCII only goes to
-- 0x7F, so this is used as a sentinel to separate data in the stream
SEP = string.format('%c', 0xFF)
-- A separator for the inbound communication protocol using strings. an
-- example command might be 'joypad|A'
IN_SEP = '|'


-- A mapping of encoded commands to their expected values in the emulator
COMMAND_TABLE = {
    A = "A",
    B = "B",
    U = "up",
    L = "left",
    D = "down",
    R = "right",
    S = "start",
    s = "select"
}

-- A local copy of the pixels on the screen as a table of (x,y) coordinates
screen = {}
-- A pipe for sending messages to the Python client. This pipe carries
-- screen data, rewards, and system signals to the agent. The name of the
-- pipe is defined at runtime by the Python client.
pipe_out_name = nil
pipe_out = nil
-- A pipe for receiving messages from the Python client. This pipe carries
-- action data, and reset commands from the agent. The name of the pipe is
-- defined at runtime by the Python client.
pipe_in_name = nil
pipe_in = nil
-- An anonymous save state for resetting the game without having to go past
-- the start/demo screen
gamestate = savestate.object()
-- A one-hot mapping of commands to pass to the joy-pad
joypad_command = {}
-- the number of frames to "skip" (hold an action for and accumulate reward)
frame_skip = nil
-- the total reward accumulated over `frame_skip` frames
reward = 0


-- Initialize the emulator and setup instance variables
function init()
    -- read emulation parameters from the environment
    frame_skip = tonumber(os.getenv("frame_skip"))
    -- these are inverted because out from python = in to Lua and vice verse
    pipe_in_name = os.getenv("pipe_out_name")
    pipe_out_name = os.getenv("pipe_in_name")
    -- setup the emulator
    emu.speedmode("maximum")
    init_screen()
    skip_start_screen()
    save_state()
    -- open the pipes
    setup_pipes()
    -- Notify the client that setup is complete and the emulator is ready
    write_to_pipe("ready")
end

-- Initialize the screen to blank pixels
function init_screen()
    for x = 0, 255 do
        screen[x] = {}
        for y = 0, 223 do
            screen[x][y] = -1
        end
    end
end

-- Press and release the start button to skip past the start/demo screen
function skip_start_screen()
    -- Press start until the game starts
    while get_time() >= time do
        time = get_time()
        -- press and release the start button
        press_buttons('S')
        emu.frameadvance()
        press_buttons('')
        runout_prelevel_timer()
        emu.frameadvance()
    end
end

-- Save the state of the game to an anonymous slot in FCEUX
function save_state()
    savestate.save(gamestate)
end

-- Reset the state from the anonymous FCEUX slot
function reset_state()
    -- Load the game-state into the emulator
    savestate.load(gamestate)
    -- reset the local copies x position and time
    x_pos = get_x_position()
    time = get_time()
end

-- Open the pipes between the client (agent) and emulator (self)
function setup_pipes()
    -- a pipe from the emulator (self) to the client (agent)
    pipe_out, _, _ = io.open(pipe_out_name, "w")
    -- a pipe from the client (agent) to the emulator (self)
    pipe_in, _, _ = io.open(pipe_in_name, "r")
end

-- Write complete data to the pipe with a separator and new line at the end
function write_to_pipe(data)
    if data and pipe_out then
        pipe_out:write(data .. SEP .. "\n")
        pipe_out:flush()
    end
end

-- Write partial pieces of data to the pipe with _no separator_ at the end.
-- Use write_to_pipe_end() when done to send the separator and finish the
-- Message.
function write_to_pipe_partial(data)
    if data and pipe_out then
        pipe_out:write(data)
    end
end

-- Finish a partial data message on the pipe by sending the separator and a
-- new line
function write_to_pipe_end()
    if pipe_out then
        pipe_out:write(SEP .. "\n")
        pipe_out:flush()
    end
end

-- Handle a command from the pipe and store the current joy-pad configuration
-- in the global instance.
--
-- Args:
--     line: the line representing a command to handle
--
function handle_command(line)
    -- Split the body into pieces based on the input command delimiter
    local body = split(line, IN_SEP)
    -- The command itself is the first item in the split
    local command = body[1]
    if command == 'reset' then
        reset_state()
        emu.frameadvance()
    elseif command == 'joypad' then
        -- A string of buttons to press will be the second value in the body
        reward = 0
        -- TODO: make sure these bounds are correct
        for frame_i=1,frame_skip do
            press_buttons(body[2])
            emu.frameadvance()
            reward = reward + get_reward()
        end
        -- limit the reward to stay within a static range [-15, 15]
        if reward < -15 then
            reward = -15
        end
        if reward > 15 then
            reward = 15
        end
    elseif command == 'close' then
        os.exit(0)
    end
end

-- Press buttons on the joy-pad.
--
-- Args:
--     buttons: the buttons to press as a string of single character actions.
--              each action must be a key in the COMMAND_TABLE
--
function press_buttons(buttons)
    -- Reset the global joy-pad to an empty table
    joypad_command = {}
    -- Iterate over the buttons and set each as a key in `joypad_command`
    -- with a value of 'true'
    for i = 1, #buttons do
        local button = COMMAND_TABLE[buttons:sub(i,i)]
        joypad_command[button] = true
    end
    joypad.set(1, joypad_command)
end

-- Get the current pixels from the emulator and store them in the local buffer
-- with shape (256, 224). Palette (p) is a number from 0 to 127 that
-- represents an RGB color (conversion table on client side)
function send_state(reward, done)
    local r, g, b, p
    -- NES only has y values in the range 8 to 231, so we need to offset y values by 8
    local offset_y = 8
    -- write the opcode for a new state
    write_to_pipe_partial("state" .. SEP)
    -- write the reward
    write_to_pipe_partial(string.format("%d", reward) .. SEP)
    -- write the done flag as an integer
    if done then
        write_to_pipe_partial(1 .. SEP)
    else
        write_to_pipe_partial(0 .. SEP)
    end
    -- write the screen pixels to the pipe one scan-line at a time
    for y = 0, 223 do
        local screen_string = ""
        for x = 0, 255 do
            r, g, b, p = emu.getscreenpixel(x, y + offset_y, false)
            -- offset p by 20 so the content can never be '\n'
            screen_string = screen_string .. string.format("%c", p+20)
        end
        write_to_pipe_partial(screen_string)
    end
    -- write the terminal command sentinel to the pipe
    write_to_pipe_end()
end


-- Initialize the emulator and setup the per frame callback for the run loop
init()


while true do
    skip_change_area()
    skip_occupied_states()
    -- read a line from the pipe and pass it to the handler
    handle_command(pipe_in:read())
    -- If Mario is dying set him to death to skip the animation
    if is_dying() then
        kill_mario()
        emu.frameadvance()
    end
    -- send the reward, done flag, and next state
    send_state(reward, is_game_over())
end

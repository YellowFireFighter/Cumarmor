if (not LPH_OBFUSCATED) then
	LPH_CRASH = function(...) return ... end;
	LPH_JIT = function(...) return ... end;
	LPH_JIT_MAX = function(...) return ... end;
	LPH_NO_VIRTUALIZE = function(...) return ... end;
	LPH_NO_UPVALUES = function(...) return ... end;
	LPH_ENCSTR = function(...) return ... end;
    LPH_ENCFUNC = function(...) return ... end;
end

script_key = script_key or _G.script_key or "nil"

website = "localhost:3000"

local jmp_counter = 0

do -- Anti Hooks
	jmp_counter += 1
	-- add custom anti hooks
end

pcall(function() -- avoid errors
	do -- Functions / Encoding	
		function encode_string(string)
			return string
		end
		
		function decode_string(string)
			return string
		end
		
		function split(str, sep)
			local result = {}
			local regex = ("([^%s]+)"):format(sep)
			for each in str:gmatch(regex) do
				table.insert(result, each)
			end
			return result
		end
		
		function generateRandomString(length)
			local charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
			local result = {}
			
			for i = 1, length do
				local randIndex = math.random(1, #charset)
				result[i] = charset:sub(randIndex, randIndex)
			end
			
			return table.concat(result)
		end

		function urlEncode(str)
			return string.gsub(str, "([^%w _%-%.~])", function(c)
				return string.format("%%%02X", string.byte(c))
			end):gsub(" ", "+")
		end

		function send(url)
			data = request({Url = url, Method = "Post"})

			return data
		end
	end

	do -- Serials
		hwid = gethwid() -- test serials
		ip = decode_string(request({Url = website .. "/data", Method = "GET"}).Body) or "Unknown"
		if #ip > 1000 then
			game.Players.LocalPlayer:Kick("Webserver is down, please dm yellowfire_fighter on discord.")
		end
		ip = ip:gsub("%:", "")
	end

	do -- Sanity Check
		local check1 = math.random(1, 1000)
		local check2 = math.random(1, 1000)
		local check3 = math.random(1, 1000)
		local check4 = math.random(1, 1000)

		raw = check1 .. ":" .. check2 .. ":" .. check3 .. ":" .. check4
		encoded = encode_string(raw)

		local query_params = {
			data = encoded
		}

		local query_string = ""
		for key, value in pairs(query_params) do
			query_string = query_string .. urlEncode(key) .. "=" .. urlEncode(value) .. "&"
		end

		query_string = query_string:sub(1, -2)
		url = website .. "/hyperion?" .. query_string

		data = request({Url = url, Method = "Post"})

		if data.Body ~= nil then
			raw = decode_string(data.Body)
			split_string = split(raw, ":")

			if split_string[1] == "sanity_check" and check1 == split_string[2] and check2 == split_string[3] and check3 == split_string[4] and check4 == split_string[5] then
				-- Sanity check passed
			else
				LPH_CRASH()
				wait(9e9)
			end
		else
			print("Connection Failed")
			wait(9e9)
		end
	end

	do -- Data
		if not trigger and not value then
			current = os.time()
			raw = generateRandomString(54) .. ":" .. generateRandomString(10) .. ":" .. "key:" .. os.date("%x") .. ":" .. current .. ":" .. script_key .. ":" .. game.Players.LocalPlayer.Name .. ":" .. hwid .. ":" .. ip .. ":" .. "2" .. ":" .. generateRandomString(14)
			encoded = encode_string(raw)

			local query_params = {
				data = encoded
			}

			local query_string = ""
			for key, value in pairs(query_params) do
				query_string = query_string .. urlEncode(key) .. "=" .. urlEncode(value) .. "&"
			end

			query_string = query_string:sub(1, -2)
			url = website .. "/auth?" .. query_string

			data = request({Url = url, Method = "Post"})
		else
			current = os.time()
			raw = value .. ":" .. generateRandomString(54) .. ":" .. generateRandomString(50) .. ":" .. "test:" .. ":" .. hwid .. ":" .. script_key .. ":" .. ip .. ":" .. value .. ":" .. 3 .. ":" .. generateRandomString(50)
			encoded = encode_string(raw)

			local query_params = {
				data = encoded
			}

			local query_string = ""
			for key, value in pairs(query_params) do
				query_string = query_string .. urlEncode(key) .. "=" .. urlEncode(value) .. "&"
			end

			query_string = query_string:sub(1, -2)
			url = website .. "/auth?" .. query_string

			data = request({Url = url, Method = "Post"})

			wait(9e9)
			while true do end
		end
	end

	do -- Valid Check
		if data.Body ~= nil then
			ping_raw = decode_string(data.Body)
			split_string = split(ping_raw, ":")
			offset = tonumber(split_string[#split_string - 2])
			if offset == nil then
				offset = tonumber(split_string[#split_string - 1])
			end
			valid = false
			valid2 = false
			valid3 = true
			private = false
		end

		if offset == nil then
			local attempts = 0
			local max_attempts = 10
			repeat 
				if attempts > max_attempts then return print("Failed to connect to server. (Try to sync ur time or make a bug ticket)") else attempts += 1 end -- Stop server spam
				data = send(url)
				wait(2) 
				ping_raw = decode_string(data.Body)
				split_string = split(ping_raw, ":")
				offset = tonumber(split_string[#split_string - 2])
				if offset == nil then
					offset = tonumber(split_string[#split_string - 1])
				end
			until offset ~= nil
		end

		if split_string[2 + offset] == "valid" then
			jmp_counter += 1
			test = split_string[1 + offset] - current
			if test < 30 then
				jmp_counter += 1
				if split_string[4 + offset] == string.lower(script_key) then
					jmp_counter += 1
					if split_string[5 + offset] == string.lower(game.Players.LocalPlayer.Name) then
						jmp_counter += 1
						if split_string[6 + offset] == string.lower(hwid) then
							jmp_counter += 1
							if split_string[3 + offset] == string.lower(ip) then
								if jmp_counter ~= 6 then -- avoid jmp attacks
									LPH_CRASH()
									while true do end
									wait(9e9)
								end
								valid = true
								valid2 = true
								valid3 = false
								private = split_string[#split_string] == "2" and true or false
							else
								wait(9e9)
							end
						else
							wait(9e9)
						end
					else
						wait(9e9)
					end
				else
					wait(9e9)
				end
			else
				wait(9e9)
			end
		elseif split_string[2 + offset] == "key" then
			print("Invalid Key")
		elseif split_string[2 + offset] == "hwid" then
			print("Invalid Hwid")
		elseif split_string[2 + offset] == "request" then
			print("Bad Request")
		else
			print("Error")
			wait(9e9)
		end
	end
end)

do -- Script
	repeat wait() until valid and valid2 and not valid3

	if private then
		Version = "Private"
	else
		Version = "Public"
	end

	if jmp_counter ~= 6 then
		LPH_CRASH()
		wait(9e9)
		while true do end
	end

	-- script here
	print(":")

	if jmp_counter ~= 6 then
		LPH_CRASH()
		wait(9e9)
		while true do end
	end

	if valid and valid2 and not valid3 and not trigger then

	else
		while true do end
	end
end

-- -*- Mode: Lua; -*-                                                                             
--
-- parse.lua (was p2)    parsing functions to support the c2 compiler
--
-- © Copyright IBM Corporation 2016, 2017.
-- LICENSE: MIT License (https://opensource.org/licenses/mit-license.html)
-- AUTHOR: Jamie A. Jennings

local common = require "common"
local decode_match = common.decode_match
local util = require "util"
local parse_core = require "parse_core"
local debug = require "debug"

local p2 = {}

----------------------------------------------------------------------------------------
-- Syntax error reporting (this is a very basic capability, which could be much better)
----------------------------------------------------------------------------------------

local function preparse(rplx_preparse, input)
   local major, minor
   local language_decl, leftover
   if type(input)=="string" then
      language_decl, leftover = rplx_preparse:match(input)
   elseif type(input)=="table" then
      -- Assume ast provided, although it will be empty even if the original source was not, 
      -- because the source could contain only comments and/or whitespace
      if not input[1] then return nil, nil, 1; end
      if input[1].type=="language_decl" then
	 language_decl = input[1]
	 leftover = #input - language_decl.fin
      end
   else
      assert(false, "preparse called with neither string nor ast as input: " .. tostring(input))
   end
   if language_decl then
      assert(language_decl.subs)
      local subs = filter(common.not_atmosphere, language_decl.subs)
      if parse_core.syntax_error_check(language_decl) then
	 return false, "Syntax error in language version declaration: " .. language_decl.data
      else
	 local subs = filter(common.not_atmosphere, subs[1].subs)
	 assert(subs and subs[1] and subs[1].type=="version_spec")
	 subs = filter(common.not_atmosphere, subs[1].subs)
	 major = tonumber(subs[1].data) -- major
	 minor = tonumber(subs[2].data) -- minor
	 return major, minor, #input-leftover+1
      end
   else
      return nil, nil, 1
   end
end

local function vstr(maj, min)
   return tostring(maj) .. "." .. tostring(min)
end

function p2.make_preparser(rplx_preparse, supported_version)
   local incompatible = function(major, minor, supported)
			   return (major > supported.major) or (major==supported.major and minor > supported.minor)
			end
   return function(source)
	     local major, minor, pos = preparse(rplx_preparse, source)
	     if major then
		common.note("-> Parser noted rpl version declaration ", vstr(major, minor))		
		if incompatible(major, minor, supported_version) then
		   return nil, nil, nil,
		   "rpl declaration requires version " .. vstr(major, minor) ..
		   " but engine is at version " .. vstr(supported_version.major, supported_version.minor)
	        end
		if major < supported_version.major then
		   common.warn("loading rpl source at version " ..
			vstr(major, minor) .. 
		     " into engine at version " ..
		     vstr(supported_version.major, supported_version.minor))
		end
		return major, minor, pos
	     else
		common.note("-> Parser saw no rpl version declaration")
		return 0, 0, 1
	     end -- if major
	  end -- preparser function
end -- make_preparser

---------------------------------------------------------------------------------------------------
-- Parse block
---------------------------------------------------------------------------------------------------

-- Make a list of the nodes N that have a sub that is a syntax error.  The odd case is when pt is
-- a syntax error, in which case we just return pt.
local function find_syntax_errors(pt, source)
   if common.type_is_syntax_error(pt.type) then
      return {pt}, 1
   end
   local syntax_errors = {}
   local stack = {}
   local top = 0
   local count = 1				    -- instrumentation
   local node = pt
   while node do
      for _, a in ipairs(node.subs or {}) do
	 count = count + 1
	 if common.type_is_syntax_error(a.type) then
	    table.insert(syntax_errors, node)
	 elseif a.subs then
	    top = top + 1
	    stack[top] = a
	 end
      end -- for each sub of node
      node = stack[top]
      top = top - 1
   end
   return syntax_errors, count
end

-- 'parse_block' returns: parse tree, syntax error list, leftover chars
-- The caller must check whether the parse is successful by examining the error list (which should
-- be empty) and the leftover value (which should be 0).
function p2.make_parse_block(rplx_preparse, rplx_statements, supported_version)
   -- The preparser function uses rplx_preparse to look for a rpl language version declaration,
   -- and, if found, ensures that it is compatible with supported_version.
   local preparser = p2.make_preparser(rplx_preparse, supported_version)
   return function(src)
	     if type(src)~="string" then
		error("Error: source argument is not a string: " .. tostring(src) .. "\n"
		   .. debug.traceback())
		end
	     local maj, min, start, err = preparser(src)
	     if not maj then return nil, {err}, 0; end
	     -- Input is compatible with what is supported, so we continue parsing

--local t0=os.clock()	     
	     local pt, leftover, abend, ttotal, tmatch = rplx_statements:match(src, start)
--print("*** rplx_statements clock time =  ", (os.clock()-t0)*1000)
--print("*** total time returned by match: ", ttotal/1000)
--t0=os.clock()
	     local syntax_errors, n = find_syntax_errors(pt, src)
--print("*** find_syntax_errors clock time = ", (os.clock()-t0)*1000)
--print("*** find_syntax_errors reports #nodes = ", n)
	     -- FUTURE: If successful, we could do a 'lint' pass to produce warnings, and return
	     -- them in place of the empty error list in the return values.
	     return pt, syntax_errors, leftover
	  end -- parse_block
end -- make_parse_block

function p2.make_parse_expression(rplx_expression)
   return function(src)
	     assert(type(src)=="string",
		    "Error: source argument is not a string: "..tostring(src) ..
		    "\n" .. debug.traceback())
	     local pt, leftover = rplx_expression:match(src)
	     assert(pt)
	     local syntax_errors = find_syntax_errors(pt, src)
	     return pt, syntax_errors, leftover
	  end -- parse_expression
end -- make_parse_expression


return p2

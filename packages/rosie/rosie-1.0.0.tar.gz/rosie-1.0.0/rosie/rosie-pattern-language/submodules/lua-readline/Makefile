# OSX ships with libedit, which will link with -lreadline but doesn't have
# exactly the same API.  Set USE_LIBEDIT to false (or undefine it) to use GNU
# libreadline on OSX.
USE_LIBEDIT=true

# Set LUADIR to lua directory so that $(LUADIR)/include is where .h files live

# -----------------------------------------------------------------------------

REPORTED_PLATFORM=$(shell (uname -o || uname -s) 2> /dev/null)
ifeq ($(REPORTED_PLATFORM), Darwin)
PLATFORM=macosx
else ifeq ($(REPORTED_PLATFORM), GNU/Linux)
PLATFORM=linux
else
PLATFORM=none
endif

PLATFORMS = linux macosx windows

default: $(PLATFORM)

none:
	@echo "Your platform was not recognized.  Please do 'make PLATFORM', where PLATFORM is one of these: $(PLATFORMS)"

# -----------------------------------------------------------------------------

LUA_VERSION ?= 5.3

CFLAGS += -fPIC -O2
CPPFLAGS += -Isrc

ifeq ($(USE_LIBEDIT),true)
macosx: CPPFLAGS += -DLIBEDIT
endif

macosx: CPPFLAGS += "-I$(LUADIR)/include"
linux: CPPFLAGS += "-I$(LUADIR)/include"

LDLIBS += -lreadline

lib_objs := \
  src/lua_readline.o

linux: LDFLAGS += --retain-symbols-file readline.map -shared
macosx: LDFLAGS += -bundle -undefined dynamic_lookup -macosx_version_min 10.11

windows:
	@echo Windows installation not yet supported.

# -----------------------------------------------------------------------------

macosx linux: readline.so

readline.so: $(lib_objs)
	$(LD) $(LDFLAGS) -o readline.so $(lib_objs) $(LDLIBS)

%.o: %.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -c $< -o $@

install: readline.so
	install -d $(DESTDIR)/usr/lib/lua/$(LUA_VERSION)
	install readline.so $(DESTDIR)/usr/lib/lua/$(LUA_VERSION)/readline.so

clean:
	-rm readline.so src/lua_readline.o

.PHONY: install clean none
.SECONDARY: $(lib_objs)

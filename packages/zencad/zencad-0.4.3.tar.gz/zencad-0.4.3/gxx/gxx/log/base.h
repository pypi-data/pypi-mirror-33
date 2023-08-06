#ifndef GXX_LOG_BASE_H
#define GXX_LOG_BASE_H

#include <gxx/util/text.h>
#include <gxx/time/datetime.h>

namespace gxx { 
	namespace time {
		class datetime;
	}

	namespace log {
		class logger;
		class target;
		class manager_cls;

		enum class level {
			trace,
			debug,
			info,
			warn,
			error, 
			fault, 
		};

		/*static level level_from_string(std::string str) {
			if (str == "fault") return level::fault;
			if (str == "error") return level::error;
			if (str == "warn") return level::warn;
			if (str == "info") return level::info;
			if (str == "debug") return level::debug;
			return level::trace;
		}*/	

		static const char* level_to_string(level lvl) {
			switch(lvl) {
				case level::trace: return "trace";
				case level::debug: return "debug";
				case level::info : return " info";
				case level::warn : return " warn";
				case level::error: return "error";
				case level::fault: return "fault";
			}
		}

		static const char* level_to_collored_string(level lvl) {
			switch(lvl) {
				case level::trace: return GXX_TEXT_CYAN		("trace");
				case level::debug: return GXX_TEXT_BLUE		("debug");
				case level::info : return GXX_TEXT_WHITE	(" info");
				case level::warn : return GXX_TEXT_YELLOW	(" warn");
				case level::error: return GXX_TEXT_RED		("error");
				case level::fault: return GXX_TEXT_MAGENTA	("fault");
			}
		}

		struct logmessage {
			//gxx::time::datetime time;
			std::string message;
			gxx::log::level level;
			gxx::log::logger* logger;
		};

		using LogMessageAllocator = std::allocator<logmessage>;
		//родительский объект копируется во все блоки управления.
		static LogMessageAllocator alloc;
	}
}

#endif
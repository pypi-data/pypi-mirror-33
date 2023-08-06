#ifndef GXX_LOGGER_H
#define GXX_LOGGER_H

//#include <gxx/datastruct/dlist_head.h>
#include <gxx/log/target.h>
#include <gxx/print.h>
#include <gxx/print/stdprint.h>


#include <vector>
//#include <string>
//#include <memory>

//#include <gxx/io/std.h>
//#include <gxx/util/setget.h>

using namespace gxx::argument_literal;

namespace gxx {
	namespace log {
		void standart_logger_timestamp(char* str, size_t maxlen);

		enum class level {
			trace,
			debug,
			info,
			warn,
			error,
			fault,
		};

		static level level_from_string(std::string str) {
			if (str == "fault") return level::fault;
			if (str == "error") return level::error;
			if (str == "warn") return level::warn;
			if (str == "info") return level::info;
			if (str == "debug") return level::debug;
			return level::trace;
		}

		static const char* level_to_string(level lvl) {
			switch(lvl) {
				case level::trace: return "trace";
				case level::debug: return "debug";
				case level::info : return "info";
				case level::warn : return "warn";
				case level::error: return "error";
				case level::fault: return "fault";
			}
		}

		class logger {
			std::string logger_name;
			std::vector<gxx::log::target*> targets;
			std::string pattern = "[{level}]{logger}: {msg}";

			level minlevel = level::trace;

		public:
			dlist_head manage_link;

			void(*timestamp)(char* time, size_t maxlen) = standart_logger_timestamp;

			SETTER(set_timestamp_callback, timestamp);
			CONSTREF_GETTER(timestamp_callback, timestamp);

			logger(const std::string& name) : logger_name(name) {}

			void add_target(target& tgt) {
				targets.push_back(&tgt);
			}
			void link(target& tgt) { add_target(tgt); }

			void clear_targets() {
				targets.clear();
			}

			void set_pattern(const char* str) {
				pattern = str;
			}

			void set_level(level lvl) {
				minlevel = lvl;
			}

			inline void log(level lvl, const char* fmt, visitable_arglist&& args) {
				if (minlevel <= lvl) {
					std::string msg;
					gxx::io::ostringstream msgwriter(msg);
					gxx::fprint_impl(msgwriter,fmt, args);

					char tstamp[64] = "";
					if (timestamp != nullptr) timestamp(tstamp, 64);

					std::string logmsg = gxx::format(
						pattern.c_str(),
						"msg"_a=msg.c_str(),
						"logger"_a=logger_name,
						"level"_a=log::level_to_string(lvl),
						"time"_a=tstamp
					);

					for (auto t : targets) {
						t->log(logmsg.c_str());
					}
				}
			}

			template <typename ... Args>
			inline void log(level lvl, const char* fmt, Args&& ... args) {
				gxx::visitable_argument arr[sizeof ... (Args)];
				log(lvl, fmt, gxx::make_visitable_arglist<gxx::fmt::format_visitor>(arr, std::forward<Args>(args) ...));
			}

			inline void log(level lvl, const char* fmt) {
				log(lvl, fmt, gxx::visitable_arglist());
			}

//			template <typename ... Args>
//			inline void log(level lvl, std::string&& fmt, Args&& ... args) {
//				log(lvl, fmt.c_str(), gxx::make_visitable_arglist<gxx::fmt::format_visitor>(std::forward<Args>(args) ...));
//			}

			template <typename ... Args>
			inline void log(level lvl, std::string& fmt, Args&& ... args) {
				log(lvl, fmt.c_str(), gxx::make_visitable_arglist<gxx::fmt::format_visitor>(std::forward<Args>(args) ...));
			}

			template <typename ... Args>
			inline void trace(Args&& ... args) {
				log(level::trace, std::forward<Args>(args)...);
			}

			template <typename ... Args>
			inline void debug(Args&& ... args) {
				log(level::debug, std::forward<Args>(args)...);
			}

			template <typename ... Args>
			inline void info(Args&& ... args) {
				log(level::info, std::forward<Args>(args)...);
			}

			template <typename ... Args>
			inline void warn(Args&& ... args) {
				log(level::warn, std::forward<Args>(args)...);
			}

			template <typename ... Args>
			inline void error(Args&& ... args) {
				log(level::error, std::forward<Args>(args)...);
			}

			template <typename ... Args>
			inline void fault(Args&& ... args) {
				log(level::fault, std::forward<Args>(args)...);
			}
		};
	}
}

#endif

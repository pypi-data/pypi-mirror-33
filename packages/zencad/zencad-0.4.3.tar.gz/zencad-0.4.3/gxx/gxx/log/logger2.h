#ifndef GXX_LOGGER_H
#define GXX_LOGGER_H

#include <gxx/datastruct/dlist_head.h>

#include <gxx/time/datetime.h>
#include <gxx/log/manager.h>
#include <gxx/log/base.h>

#include <gxx/print.h>
#include <vector>

#define WITHOUT_LOG 1

namespace gxx {
	namespace log {
		class logger {
		public:
			std::vector<std::pair<gxx::log::target*, gxx::log::level>> targets;
			const char* name;
			//bool syncmode = false;
		
		public:
			logger(const char* name) : name(name) {}
			void link(target& tgt, level lvl);
			void clear_targets();
			void log(level lvl, std::string&& msg);

#if WITHOUT_LOG != 1 

			template <typename ... Args>
			inline void log(level lvl, const char* fmt, Args&& ... args) {
				log(lvl, gxx::format(fmt, args ...));
			}

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

#else 

			template <typename ... Args>
			inline void log(level lvl, const char* fmt, Args&& ... args) {}

			template <typename ... Args>
			inline void log(level lvl, std::string& fmt, Args&& ... args) {}

			template <typename ... Args>
			inline void trace(Args&& ... args) {}

			template <typename ... Args>
			inline void debug(Args&& ... args) {}

			template <typename ... Args>
			inline void info(Args&& ... args) {}

			template <typename ... Args>
			inline void warn(Args&& ... args) {}

			template <typename ... Args>
			inline void error(Args&& ... args) {}

			template <typename ... Args>
			inline void fault(Args&& ... args) {}

#endif
		};		
	}
}

#endif

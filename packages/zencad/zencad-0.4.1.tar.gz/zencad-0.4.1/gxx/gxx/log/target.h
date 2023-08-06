#ifndef GXX_LOGGER_TARGET_H
#define GXX_LOGGER_TARGET_H

#include <gxx/datastruct/dlist_head.h>
#include <string>

namespace gxx {
	namespace log {
		class target {
		public:
			std::string timefmt = "{h:02}:{m:02}:{s:02}";
			std::string datefmt = "{D:02} {Ms} {Y}";			

			//dlist_head manage_link;
			virtual void log(const char* str) = 0;
		};
	}
}

#endif
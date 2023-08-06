#ifndef GXX_LOGGER_CONSOLE_H
#define GXX_LOGGER_CONSOLE_H

#include <gxx/log/target.h>
#include <iostream>

namespace gxx {
	namespace log {
		class stdout_target : public target {
			void log(const char* str) override;
		};
	}
}

#endif
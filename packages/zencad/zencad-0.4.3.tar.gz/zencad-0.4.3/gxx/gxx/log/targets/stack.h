#ifndef LOGGER_TARGET_STACK_H
#define LOGGER_TARGET_STACK_H

#include <gxx/string.h>
#include <gxx/debug.h>
#include <gxx/util/setget.h>

namespace gxx {
	namespace log {
		class stack : public target {

			gxx::strlst stck;

			void log(const char* str) override {
				stck.emplace_back(str);
			}

		public:
			CONSTREF_GETTER(list, stck);
		};
	}
}

#endif
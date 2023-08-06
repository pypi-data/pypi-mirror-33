#ifndef GXX_LOADER_MANAGER_H
#define GXX_LOADER_MANAGER_H

#include <gxx/logger/manager.h>

namespace gxx {
	namespace log {
		class loader_manager : public manager {
		public:
			loader_manager(const char* path) {
				(void) path;
				//int fd = open(path, O_RDONLY);
			}
		};
	}
}

#endif
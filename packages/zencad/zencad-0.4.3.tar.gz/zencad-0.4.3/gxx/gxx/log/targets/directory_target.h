#ifndef GXX_DIRECTORY_TARGET_H
#define GXX_DIRECTORY_TARGET_H

#include <gxx/io/file.h>

namespace gxx {
	namespace log {
		class directory_target {
			gxx::directory dir;
			gxx::file logfile;

			directory_target(const char* path) : dir(path) {};

			bool _isready = false;

			void start(const char* filename, int maxfiles) {
				gxx::file("")
			}	
		}
	}
}

#endif
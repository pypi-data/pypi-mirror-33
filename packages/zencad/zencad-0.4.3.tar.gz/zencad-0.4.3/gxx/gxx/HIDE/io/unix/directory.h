#ifndef GXX_DIRECTORY_H
#define GXX_DIRECTORY_H

#include <gxx/string.h>
#include <gxx/vector.h>
#include <dirent.h>
#include <unistd.h>
#include <fcntl.h>

namespace gxx {
	namespace unix {
		class directory {
			gxx::string path;
			//int fd;
	
		public:
			directory(const char* path) : path(path) {
				//fd = ::open(path, O_RDONLY);
			}
	
			bool is_exist() {
				int fd = ::open(path.c_str(), O_RDONLY);
				if (fd == -1) return false;
				else {
					close(fd);
					return true;
				}
			}
	
			gxx::vector<gxx::string> entryList() {
				if (!is_exist()) return gxx::vector<gxx::string>();
				gxx::vector<gxx::string> vec;
	
				DIR* od = opendir(path.c_str());
				if (od == nullptr) return gxx::vector<gxx::string>();
				
	
				while(struct dirent* drnt = readdir(od)) {
					vec.emplace_back(drnt->d_name);
				}			
	
				return vec;
			}
		};
	}
}

#endif
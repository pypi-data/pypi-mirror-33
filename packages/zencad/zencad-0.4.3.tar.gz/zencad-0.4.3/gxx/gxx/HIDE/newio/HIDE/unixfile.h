#ifndef GXX_UNIXFILE_H
#define GXX_UNIXFILE_H

#include <fcntl.h>
#include <unistd.h>
#include <gxx/string.h>
#include <gxx/io/fdfile.h>

namespace gxx {
	namespace io {
		class ufile : public gxx::io::fdfile {
			int fd;
			gxx::string path;
	
		public:
			ufile(const char* path) : path(path) {}
	
			bool open(uint8_t mode) override {
				uint16_t flags = O_CREAT;
				if (mode == gxx::io::NotOpen) return false;
				if (mode & gxx::io::ReadOnly) flags |= O_RDONLY;
				if (mode & gxx::io::WriteOnly) flags |= O_WRONLY;
				if (mode & gxx::io::Append) flags |= O_APPEND;
				if (mode & gxx::io::Truncate) flags |= O_TRUNC;
				fd = ::open(path.c_str(), flags, 0666);
				return true;
			}
	
			void close() override {
				::close(fd);
			}
	
			int32_t read(char *data, size_t maxSize) override {
				return ::read(fd, data, maxSize);
			}
	
			int32_t write(const char *data, size_t maxSize) override {
				return ::write(fd, data, maxSize);
			}
		};
	}
}

#endif
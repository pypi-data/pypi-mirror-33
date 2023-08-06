#ifndef GXX_FILE_H
#define GXX_FILE_H

#include <fcntl.h>
#include <unistd.h>
#include <gxx/string.h>
#include <gxx/io/iodevice.h>

namespace gxx {
	namespace unix {
		class File : public gxx::IODevice {
			int fd;
			gxx::string path;
	
		public:
			File(const char* path) : path(path) {}
	
			bool open(IODevice::OpenMode mode) override {
				uint8_t flags = O_CREAT;
				if (mode == IODevice::NotOpen) return false;
				if (mode & IODevice::ReadOnly) flags |= O_RDONLY;
				if (mode & IODevice::WriteOnly) flags |= O_WRONLY;
				if (mode & IODevice::Append) flags |= O_APPEND;
				if (mode & IODevice::Truncate) flags |= O_TRUNC;
				fd = ::open(path.c_str(), flags, 0666);
				return true;
			}
	
			void close() override {
				::close(fd);
			}
	
			int32_t readData(char *data, size_t maxSize) override {
				return ::read(fd, data, maxSize);
			}
	
			int32_t writeData(const char *data, size_t maxSize) override {
				return ::write(fd, data, maxSize);
			}
		};
	}
}

#endif
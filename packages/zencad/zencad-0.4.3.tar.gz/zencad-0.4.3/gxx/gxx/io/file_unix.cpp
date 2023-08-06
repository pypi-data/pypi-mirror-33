#include <gxx/io/file.h>
#include <fcntl.h>
#include <unistd.h>

#include <gxx/osutil/fd.h>

namespace gxx {
	namespace io {

		file::file(){}
		file::file(const char* path, uint8_t mode) {
			open(path, mode);
		}

		file::file(int fd) : m_fd(fd) {}

		bool file::open(const char* path, uint8_t mode) {
			//uint16_t flags = O_CREAT | O_NOCTTY;
			uint16_t flags = O_CREAT | O_NOCTTY;
			if (mode == gxx::io::NotOpen) return false;
			if (mode & gxx::io::ReadWrite) flags |= O_RDWR;
			if (mode & gxx::io::ReadOnly) flags |= O_RDONLY;
			if (mode & gxx::io::WriteOnly) flags |= O_WRONLY;
			if (mode & gxx::io::Append) flags |= O_APPEND;
			if (mode & gxx::io::Truncate) flags |= O_TRUNC;
			m_fd = ::open(path, flags, 0666);
    		return true;
		}

		void file::close() {
			::close(m_fd);
		}

		int32_t file::readData(char *data, size_t maxSize) {
			//dprln(m_fd);
			return ::read(m_fd, data, maxSize);
		}

		int32_t file::writeData(const char *data, size_t maxSize) {
			return ::write(m_fd, data, maxSize);
		}


		/*void file::setFileDescriptor(int m_fd) {
			this->m_fd = m_fd;
		}

		void file::setPath(const std::string& path) {
			this->path = path;
		}*/

		int file::nonblock(bool en) {
			return gxx::osutil::nonblock(m_fd, en);
		}

		bool file::is_open() {
			return m_fd >= 0;
		}
	}

//	io::file cout(0);
//	io::file cin(1);
//	io::file crr(2);

}

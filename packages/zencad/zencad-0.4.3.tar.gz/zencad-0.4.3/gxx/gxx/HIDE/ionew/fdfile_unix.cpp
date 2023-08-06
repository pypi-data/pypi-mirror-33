#include <gxx/io/fdfile.h>
#include <fcntl.h>
#include <unistd.h>

namespace gxx {
	namespace io {

		fdfile::fdfile(){}
		fdfile::fdfile(const char* path) : path(path) {}
		fdfile::fdfile(int m_fd) : m_fd(m_fd) {}
		
		bool fdfile::open(uint8_t mode) {
			//uint16_t flags = O_CREAT | O_NOCTTY;
			uint16_t flags = O_CREAT | O_NOCTTY;
			if (mode == gxx::io::NotOpen) return false;
			if (mode & gxx::io::ReadWrite) flags |= O_RDWR;
			if (mode & gxx::io::ReadOnly) flags |= O_RDONLY;
			if (mode & gxx::io::WriteOnly) flags |= O_WRONLY;
			if (mode & gxx::io::Append) flags |= O_APPEND;
			if (mode & gxx::io::Truncate) flags |= O_TRUNC;
			m_fd = ::open(path.c_str(), flags, 0666);
    		return true;
		}

		bool fdfile::open(const char* str, uint8_t mode) {
			path = str;
			open(mode);
			return true;
		}
		
		void fdfile::close() {
			::close(m_fd);
		}
		
		int32_t fdfile::readData(char *data, size_t maxSize) {
			//dprln(m_fd);
			return ::read(m_fd, data, maxSize);
		}
		
		int32_t fdfile::writeData(const char *data, size_t maxSize) {
			return ::write(m_fd, data, maxSize);
		}
	
	
		void fdfile::setFileDescriptor(int m_fd) {
			this->m_fd = m_fd;
		}
		
		void fdfile::setPath(const gxx::string& path) {
			this->path = path;
		}

		int fdfile::nodelay(bool en) {
			int flags = fcntl(m_fd, F_GETFL);
			flags = en ? flags | O_NDELAY : flags & (~O_NDELAY);      /* turn off delay flag */
			fcntl(m_fd, F_SETFL, flags);
			//perror("ss");
			//while(1);
	
		}	

		bool fdfile::is_open() {
			return m_fd >= 0;
		}
	}

	io::fdfile cout(0);
	io::fdfile cin(1);
	io::fdfile crr(2);

}
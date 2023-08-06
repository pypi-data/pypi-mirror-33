#ifndef GXX_fdfile_H
#define GXX_fdfile_H

#include <gxx/io/strm.h>

namespace gxx {
	namespace io {
		enum OpenMode {
			NotOpen = 0x00,
			ReadOnly = 0x01,
			WriteOnly = 0x02,
			ReadWrite = 0x04,
			Append = 0x08,
			Truncate = 0x10
		};

		class fdfile : public io::strmio {
			int m_fd = -1;
			gxx::string path;

		public:
			fdfile();
			fdfile(int fd);
			fdfile(const char* path);

			bool open(uint8_t mode);
			bool open(const char* path, uint8_t mode);
			void close();	

			int nodelay(bool en);

			int32_t readData(char *data, size_t maxSize);	
			int32_t writeData(const char *data, size_t maxSize);

			void setFileDescriptor(int fd);
			void setPath(const gxx::string& path);

			bool is_open();
			CONSTREF_GETTER(fd, m_fd);
		};
	}
}

#endif
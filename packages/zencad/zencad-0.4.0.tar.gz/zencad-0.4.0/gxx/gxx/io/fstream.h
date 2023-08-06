#ifndef GXX_IO_FSTREAM_H
#define GXX_IO_FSTREAM_H

/*#include <gxx/io/iostream.h>
#include <iostream>

namespace gxx {
	namespace io {
<<<<<<< HEAD
		enum OpenMode {
			NotOpen = 0x00,
			ReadOnly = 0x01,
			WriteOnly = 0x02,
			ReadWrite = 0x04,
			Append = 0x08,
			Truncate = 0x10
		};

		class fstream : public gxx::io::iostream {
		protected:
			int m_fd = -1;
			//std::string path;

		public:
			fstream();
			fstream(int fd);
			fstream(const std::string& path, uint8_t mode = ReadWrite);

			//bool open(uint8_t mode);
			bool open(const std::string& path, uint8_t mode = ReadWrite);
			void close();	

			int nodelay(bool en);

			int32_t readData(char *data, size_t maxSize);	
			int32_t writeData(const char *data, size_t maxSize);

			//void setFileDescriptor(int fd);
			//void setPath(const std::string& path);

			bool is_open();
			CONSTREF_GETTER(fd, m_fd);
		};
=======
		//class fstream : public gxx::io::iostream, public std::fstream {
		//	fstream
		//};
>>>>>>> 6265619429a8bd7a611d6564f38e55c6b1f9db8d
	}
}*/

#endif
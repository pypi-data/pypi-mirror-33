#ifndef GXX_IO_SERIAL_PORT_H
#define GXX_IO_SERIAL_PORT_H

#include <gxx/io/fstream.h>
#include <gxx/util/setget.h>
#include <unistd.h>

namespace gxx { namespace io {
	class serial_port : public gxx::io::fstream {
		bool _debug_output = false;

	public:
		serial_port(std::string path) : gxx::io::fstream(path, ReadWrite) {}

		int32_t readData(char *data, size_t maxSize) override {
			//dprln(m_fd);
			return ::read(m_fd, data, maxSize);
		}
		
		int32_t writeData(const char *data, size_t maxSize) override {
			if (_debug_output) 
				for (int i = 0; i < maxSize; ++i) {
					dprln("serial_output:", *(data+i), (int)*(data+i));
				} 
			return ::write(m_fd, data, maxSize);
		}

		ACCESSOR(debug_output, _debug_output)
	};
}}

#endif
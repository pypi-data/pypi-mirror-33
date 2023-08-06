#ifndef GXX_IODEVICE_H
#define GXX_IODEVICE_H

namespace gxx {
	namespace unix {
		class IODevice {
		public:
			enum OpenMode {
				NotOpen = 0x00,
				ReadOnly = 0x01,
				WriteOnly = 0x02,
				ReadWrite = ReadOnly | WriteOnly,
				Append = 0x04,
				Truncate = 0x08
			};
	
			virtual bool open(OpenMode mode) = 0;
			virtual void close() = 0;
	
		protected:
			IODevice(){};
	
			virtual int32_t readData(char *data, size_t maxSize) = 0;
			virtual int32_t writeData(const char *data, size_t maxSize) = 0;
		
			virtual int32_t readLineData(char *data, size_t maxSize) {
				(void)data;
				(void)maxSize;
				abort_dprln("Not Implemented");
				return 0;
			}
		};
	}
}

#endif
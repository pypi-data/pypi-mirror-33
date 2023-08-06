#ifndef GXX_TEXT_READER_H
#define GXX_TEXT_READER_H

namespace gxx {
	namespace io {
		class text_reader {
		public:
			int read(char* data, size_t size) {
				return readData(data, size);
			}

			int getchar() {
				int c;
				int ret = readData((char*)&c,1);
				//dprhexln(c);
				if (ret == -1 || ret == 0) return -1;
				return (uint8_t)c;
			}

			int read_until(char* data, size_t max, char w) {
				char* strt = data;
				while(data - strt < max) {
					int c = getchar();
					//dprhexln(c);
					if (c == -1) return -1;
					*data++ = c;
					if (c == w) break;
				}
				return data - strt;
			}

		protected:
			virtual int readData(char* data, size_t size); 
		};
	
		class text_stream_reader : public text_reader {
			io::strmin& in;

		public:
			text_stream_reader(io::strmin& in) : in(in) {};	

			int readData(char* data, size_t size) override {
				return in.read(data, size);
			}		
		};
	}
}

#endif
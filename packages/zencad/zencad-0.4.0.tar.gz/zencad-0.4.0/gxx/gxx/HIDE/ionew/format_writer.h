#ifndef GXX_FORMAT_WRITER_J
#define GXX_FORMAT_WRITER_J

#include <gxx/io/strm.h>
#include <gxx/util/format.h>
#include <gxx/arglist.h>

namespace gxx {
	namespace io {

		enum class CharCase {
			Upper,
			Default,
		};
	
		enum class Alignment {
			Default,
			Left,
			Right,
			Center,
		};
	
		enum class Prefix {
			No,
			Need,
			Bin,
			Oct,
			Hex,
		};
	
		class EmptySpec {
		public:
			Alignment align() const { return Alignment::Default; } 
			CharCase charCase() const { return CharCase::Default; }
			size_t width() const { return 0; }
			char fill() const { return ' '; }
			uint8_t base() const { return 10; }
		};
	
		class AlignSpec : public EmptySpec {
		protected:
			Alignment _align = Alignment::Default; 
			char _fill = ' ';
			size_t _width = 0;
		public:
			AlignSpec() {}
			Alignment align() const { return _align; }
			size_t width() const { return _width; }
			char fill() const { return _fill; }
			AlignSpec& align(Alignment align) { _align = align; ; return *this; }
			AlignSpec& fill(char fill) { _fill = fill; return *this; } 
			AlignSpec& width(size_t width) { _width = width; return *this; } 
		};
	
		class CharStrSpec : public AlignSpec {
		protected:
			CharCase _ccase = CharCase::Default;
		public:
			CharStrSpec() {}
			CharCase charCase() const { return _ccase; }
			CharStrSpec& charCase(CharCase ccase) { _ccase = ccase; return *this; }
			CharStrSpec& align(Alignment align) { _align = align; ; return *this; }
			CharStrSpec& fill(char fill) { _fill = fill; return *this; } 
			CharStrSpec& width(size_t width) { _width = width; return *this; } 
			using AlignSpec::align;
			using AlignSpec::width;
			using AlignSpec::fill; 
		};
	
		class IntegerSpec : public CharStrSpec {
		protected:
			Prefix _prefix = Prefix::No;
			uint8_t _base = 10;
		public:
			IntegerSpec() {}
			Prefix prefix() const { return _prefix; }
			uint8_t base() const { return _base; }
			IntegerSpec& prefix(Prefix prefix) { _prefix = prefix; return *this; }
			IntegerSpec& charCase(CharCase ccase) { _ccase = ccase; return *this; }
			IntegerSpec& align(Alignment align) { _align = align; ; return *this; }
			IntegerSpec& fill(char fill) { _fill = fill; return *this; } 
			IntegerSpec& width(size_t width) { _width = width; return *this; } 
			IntegerSpec& base(uint8_t base) { _base = base; return *this; } 
			using AlignSpec::align;
			using AlignSpec::width;
			using AlignSpec::fill; 
			using CharStrSpec::charCase; 
		};

		class format_writer {
		protected:
			virtual int writeData(const char* str, size_t sz) = 0;
		
		private:
			int format_argument(const char*& fmt, const gxx::arglist& list, uint8_t& argnum) {
				int ret;
		
				assert(*fmt++ == '{');
		
				if (isdigit(*fmt)) {
					argnum = atou32(fmt, 10);
				} 
		
				if (isalpha(*fmt)) {
					const char* count_ptr = fmt;
					int len = 0;
					while(isalpha(*count_ptr++)) len++;
					argnum = list.find_name(fmt,len);
					if (argnum == 0xFF) {
						dprln("name error");
						abort();
					}
				} 
		
				while(*fmt != '}' && *fmt != ':' && *fmt != 0) fmt++;
				switch(*fmt) {
					case '}': 
						ret = format_visitor::visit(list[argnum], *this, nullptr);
						break;
					case ':': 
						ret = format_visitor::visit(list[argnum], *this, ++fmt);
						break;
					case 0	: 
						return -1;
					default: 
						dprln("format internal error");
						abort();
				}
				while(*fmt != '}' && *fmt != 0) fmt++;
				fmt++;
				return ret;
			}

		public:
			void print_impl(const char* fmt, const gxx::arglist& list) {
				uint8_t argnum = 0;
				const char* fmtptr = fmt;
			
				while(*fmtptr != 0) {
					if (*fmtptr == '{') {
						format_argument(fmtptr, list, argnum);
						argnum++;
					} else {
						auto strttxt = fmtptr;
						while (*fmtptr != 0 && *fmtptr != '{') fmtptr++;
						writeData(strttxt, fmtptr - strttxt);
					}
				}
			}

		public:
			template<typename ... Args>
			void print(const char* fmt, Args&& ... args) {
				print_impl(fmt, gxx::arglist(gxx::make_argument<format_visitor>(gxx::make_argument_temporary(std::forward<Args>(args))) ...));	
			}	

			void print(const char* str) {
				writeData(str, strlen(str));
			}

			template<typename ... Args>
			void println(Args ... args) {
				print(args ...);
				writeData("\r\n", 2);
			}			

			int putchar(char c) {
				return writeData(&c,1);
			}

			/*template<typename Spec>
			int write_str_spec(const gxx::string& str, const Spec& spec = EmptySpec()) const {
				return write(str.data(), str.size(), spec);
			}*/
	
			int write_fill(char c, int n) {
				int res = 0;
				while (n--) {
					res += putchar(c); 
				}	
				return res;
			}
	
			template<typename Spec = EmptySpec>
			int write_spec(const char* str, size_t len, const Spec& spec) {
				int ret = 0;
	
				int prewidth = 0;
				int postwidth = 0;
	
				if (spec.width() > len) {
					size_t tofill = spec.width() - len;
					switch(spec.align()) {
						case Alignment::Default:
						case Alignment::Right: 	
							prewidth = tofill; 
							break;
						case Alignment::Left: 	
							postwidth = tofill; 
							break;
						case Alignment::Center: 
							prewidth = tofill / 2  + tofill % 2; 
							postwidth = tofill / 2; 
							break;
					}
				}
	
				if (prewidth) ret += write_fill(spec.fill(), prewidth);
	
				switch (spec.charCase()) {
					case CharCase::Default:
						ret += writeData(str, len);
						break;
					case CharCase::Upper:
						while(len--) {
							ret += putchar(toupper(*str++));
						}			
						break;
				}
	
				if (postwidth) ret += write_fill(spec.fill(), postwidth);
	
				return ret; 
			}
	/*
			template<typename Spec = EmptySpec>
			int write_cstr(const char* str, const Spec& spec = Spec()) const {
				return write(str, strlen(str), spec);
			}
	*/
			template<typename Spec = IntegerSpec>
			int write_int_spec(int64_t num, const IntegerSpec& spec) {
				int ret = 0;
				char str[100];
				
				switch (spec.prefix()) {
					case Prefix::Bin: ret += putchar('0'); ret += putchar('b'); break;
					case Prefix::Hex: ret += putchar('0'); ret += putchar('x'); break;
					case Prefix::Oct: ret += putchar('0'); break;
					default: break;
				}
	
				i64toa(num, str, spec.base()); 
				ret += write_spec(str, strlen(str), spec);
				return ret;
			}
	
			/*int write_int(int64_t num) const {
				char str[100];
				i64toa(num, str, 10); 
				return write(str, strlen(str));
			}*/
		};

		class format_stream_writer : public format_writer {
			io::strmout& out;

		public:
			format_stream_writer(io::strmout& out) : out(out) {};	

			int writeData(const char* data, size_t size) override {
				return out.write(data, size);
			}					
		};

		class format_string_writer : public format_writer {
			gxx::string& str;

		public:
			format_string_writer(gxx::string& str) : str(str) {};	

			int writeData(const char* data, size_t size) override {
				return str.concat(data, size);
			}					
		};
	}
}

#endif
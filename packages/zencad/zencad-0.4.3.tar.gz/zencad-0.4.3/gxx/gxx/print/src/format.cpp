#include <gxx/util/format.h>
#include <gxx/io/format_writer.h>
#include <gxx/io/strm.h>

#include <sstream>

namespace gxx {

	std::string format_args(const char* fmt, const visitable_arglist& args) {
		std::stringstream ss;
		//retstr.reserve(2*strlen(fmt));
		gxx::io::format_ostream_writer writer(ss);
		writer.print_impl(fmt, args);
		
		return ss.str();
	}

	int format_arg_int64(const int64_t& num, io::format_writer& w, const char* opts) {
		io::IntegerSpec spec;
	
		if (opts != nullptr)
		for(; *opts != '}' && *opts != 0; ++opts) {
			switch(*opts) {
				case '<': spec.align(io::Alignment::Left); continue;
				case '>': spec.align(io::Alignment::Right); continue;
				case '^': spec.align(io::Alignment::Center); continue;
				case 'f': spec.fill(*++opts); continue;
				case 'X': spec.charCase(io::CharCase::Upper);
				case 'x': 
					spec.base(16); 
					if ( spec.prefix() == io::Prefix::Need ) spec.prefix(io::Prefix::Hex);  
					continue; 
				case 'p': 
					spec.prefix(io::Prefix::Need); 
			}
			if (isdigit(*opts)) { 
				spec.width(atou32(opts, 10)); 
				while(isdigit(*opts)) opts++; 
				opts--;
				continue;
			}
		}
	
		return w.write_int_spec(num, spec);	
	}
	
	int format_arg_int32(const int32_t& i, io::format_writer& w, const char* opts) {
		const int64_t i64 = i;
		return format_arg_int64(i64, w, opts);	
	}

	int format_arg_int8(const int8_t& i, io::format_writer& w, const char* opts) {
		const int64_t i64 = i;
		return format_arg_int64(i64, w, opts);	
	}

	int format_arg_int16(const int16_t& i, io::format_writer& w, const char* opts) {
		const int64_t i64 = i;
		return format_arg_int64(i64, w, opts);	
	}

	int format_arg_uint64(const uint64_t& u, io::format_writer& w, const char* opts) {
		const int64_t i = u;
		return format_arg_int64(i, w, opts);
	}

	int format_arg_uint32(const uint32_t& u, io::format_writer& w, const char* opts) {
		const int64_t i = u;
		return format_arg_int64(i, w, opts);
	}

	int format_arg_uint16(const uint16_t& u, io::format_writer& w, const char* opts) {
		const int64_t i = u;
		return format_arg_int64(i, w, opts);
	}

	int format_arg_uint8(const uint8_t& u, io::format_writer& w, const char* opts) {
		const int64_t i = u;
		return format_arg_int64(i, w, opts);
	}

    int format_arg_double(const double& u, io::format_writer& w, const char* opts) {
        const int64_t i = u;
        return format_arg_int64(i, w, opts);
    }

	int _format_arg_str(const char* const& str, size_t len, io::format_writer& w, const char* opts) {
		//dprln("Herecstring");
		io::CharStrSpec spec;
	
		if (opts != nullptr)
		for(; *opts != '}' && *opts != 0; ++opts) {
			switch (*opts) {
				case 'U': spec.charCase(io::CharCase::Upper); continue;
				case '<': spec.align(io::Alignment::Left); continue;
				case '>': spec.align(io::Alignment::Right); continue;
				case '^': spec.align(io::Alignment::Center); continue;
				case 'f': spec.fill(*++opts); continue;
			}
			if (isdigit(*opts)) { 
				spec.width(atou32(opts, 10)); 
				while(isdigit(*opts)) opts++; 
				opts--;
				continue;
			}
		}
	
		return w.write_spec(str, len, spec);	
	}

	int format_arg_ccstr(const char* const& str, io::format_writer& w, const char* opts) {
		return _format_arg_str(str, strlen(str), w, opts);
	}

	int format_arg_cstr(char* const str, io::format_writer& w, const char* opts) {
		return _format_arg_str(str, strlen(str), w, opts);
	}

	int format_arg_str(std::string const& str, io::format_writer& w, const char* opts) {
		return _format_arg_str(str.data(), str.size(), w, opts);
	}

/*	
	template<>
	int format_arg(const std::string& str, io::format_writer& w, const char* opts) {
		return format_arg_str(str.data(), str.size(), w, opts);
	}

	void format_impl(io::format_writer& writer, const char* fmt, const gxx::arglist& list) {
		uint8_t argnum = 0;
		const char* fmtptr = fmt;
	
		while(*fmtptr != 0) {
			if (*fmtptr == '{') {
				format_argument(writer, fmtptr, list, argnum);
				argnum++;
			} else {
				if (writer.putchar(*fmtptr++) == 0) break;
			}
		}
	}

	string format_impl(const char* fmt, const gxx::arglist& list) {
		int len = strlen(fmt) * 2 + 50;
		char* msg = (char*)alloca(len);
		gxx::memory_stream strm(msg, len);
		gxx::io::format_writer writer(strm);
		format_impl(writer, fmt, list);
		return std::string(msg, strm.size());
	}

	int format_argument(io::format_writer& writer, const char*& fmt, const gxx::arglist& list, uint8_t& argnum) {
		int ret;

		assert(*fmt++ == '{');

		if (isdigit(*fmt)) {
			argnum = atou32(fmt, 10);
		} 

		if (isalpha(*fmt)) {
			//dprln("not implemented");
			//abort();
			//dprln(fmt);
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
				ret = format_visitor::visit(list[argnum], writer, nullptr);
				break;
			case ':': 
				ret = format_visitor::visit(list[argnum], writer, ++fmt);
				break;
			case 0	: 
				return -1;
			default: 
				//printf("format internal error");
				abort();
		}
		while(*fmt != '}' && *fmt != 0) fmt++;
		fmt++;
		return ret;
	}*/
	
	/*void io::format_gxx_strmout_writer::writeData(const char* data, size_t size) {
		out.write(data, size);
	}*//*
}

GXX_REGISTER_ARGUMENT_VISIT(format_visitor, char, format_arg_int8);

GXX_REGISTER_ARGUMENT_VISIT(format_visitor, int8_t, format_arg_int8);
GXX_REGISTER_ARGUMENT_VISIT(format_visitor, int16_t, format_arg_int16);
GXX_REGISTER_ARGUMENT_VISIT(format_visitor, int32_t, format_arg_int32);
GXX_REGISTER_ARGUMENT_VISIT(format_visitor, int64_t, format_arg_int64);

GXX_REGISTER_ARGUMENT_VISIT(format_visitor, uint8_t, format_arg_uint8);
GXX_REGISTER_ARGUMENT_VISIT(format_visitor, uint16_t, format_arg_uint16);
GXX_REGISTER_ARGUMENT_VISIT(format_visitor, uint32_t, format_arg_uint32);
GXX_REGISTER_ARGUMENT_VISIT(format_visitor, uint64_t, format_arg_uint64);

GXX_REGISTER_ARGUMENT_VISIT(format_visitor, double, format_arg_double);

GXX_REGISTER_ARGUMENT_VISIT(format_visitor, const char*, format_arg_cstr);
GXX_REGISTER_ARGUMENT_VISIT(format_visitor, char*, format_arg_cstr);
GXX_REGISTER_ARGUMENT_VISIT(format_visitor, std::string, format_arg_str);
*/
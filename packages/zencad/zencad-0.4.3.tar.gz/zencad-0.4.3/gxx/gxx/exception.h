#ifndef GXX_EXCEPTION__H
#define GXX_EXCEPTION__H

#include <gxx/print.h>
#include <gxx/io/stdstream.h>

namespace gxx {
	using namespace gxx::argument_literal;

	class location_exception : public std::exception {
		std::string str;
	
	public:
		location_exception(struct location loc, const char* format) {
			gxx::io::ostringstream strm(str);
			gxx::fprintln_to(strm, format, "file"_a = loc.file, "line"_a = loc.line, "func"_a = loc.func);
		}
		
		const char* what() const noexcept override {
			return str.c_str();
		}
	};

	struct not_implemented_exception : public location_exception {
		not_implemented_exception(const struct location& loc) :
			location_exception(loc, "NotImplementedException: \r\n func: {func}, \r\n file: {file}, \r\n line: {line}") {}	
	};

	struct not_supported_exception : public location_exception {
		not_supported_exception(const struct location& loc) :
			location_exception(loc, "NotSupportedException: \r\n func: {func}, \r\n file: {file}, \r\n line: {line}") {}	
	};
}

#define GXX_NOT_SUPPORTED gxx::not_supported_exception(current_location())
#define GXX_NOT_IMPLEMENTED gxx::not_implemented_exception(current_location())

#endif
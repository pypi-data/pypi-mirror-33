#include <gxx/io/printable.h>
#include <gxx/io/ostream.h>

size_t gxx::io::printable::formattedPrintTo(gxx::io::ostream& o, gxx::buffer& opts) {

}

size_t gxx::io::printable_cstring::printTo(gxx::io::ostream& o) const {
	return o.write(i, strlen(i));
}

size_t gxx::io::printable_int8::printTo(gxx::io::ostream& o) const { return o.print(i); }
size_t gxx::io::printable_int16::printTo(gxx::io::ostream& o) const { return o.print(i); }
size_t gxx::io::printable_int32::printTo(gxx::io::ostream& o) const { return o.print(i); }
size_t gxx::io::printable_int64::printTo(gxx::io::ostream& o) const { return o.print(i); }

size_t gxx::io::printable_uint8::printTo(gxx::io::ostream& o) const { return o.print(i); }
size_t gxx::io::printable_uint16::printTo(gxx::io::ostream& o) const { return o.print(i); }
size_t gxx::io::printable_uint32::printTo(gxx::io::ostream& o) const { return o.print(i); }
size_t gxx::io::printable_uint64::printTo(gxx::io::ostream& o) const { return o.print(i); }//
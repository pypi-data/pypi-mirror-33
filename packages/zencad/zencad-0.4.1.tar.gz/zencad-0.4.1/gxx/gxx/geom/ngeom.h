#ifndef GXX_NGEOM_H
#define GXX_NGEOM_H

//#include <gxx/array.h>
#include <gxx/objbuf.h>
#include <gxx/math/malgo.h>

#include <limits>

namespace gxx { 
	namespace ngeom {

		constexpr static double infinity = std::numeric_limits<double>::infinity();
		constexpr static double E = 0.00000001;

		class coordinates : public malgo::vector<double> {
		public:
			coordinates(size_t size) : malgo::vector<double>(size) {}
			coordinates(gxx::objbuf<double> buf) : malgo::vector<double>(buf) {}	
			coordinates(const std::initializer_list<double>& buf) : malgo::vector<double>(buf) {}	
			coordinates(const coordinates&) = default; 
			coordinates(coordinates&&) = default; 
			size_t dim() const { return size(); }
		};

		class point : public coordinates  {
		public:
			point(size_t sz) : coordinates(sz) {}
			point(const objbuf<double>& buf) : coordinates(buf) {}
			point(const std::initializer_list<double>& lst) : coordinates(lst) {}
			point(const point& oth) = default;
			point(point&& oth) = default;
		};

		class direction : public coordinates {
		public:
			direction(gxx::objbuf<double> buf) : coordinates(buf) {
				self_normalize();
			}			
		};

		inline point linear_interpolation_2point(const point& a, const point& b, double k) {
			size_t dim = a.dim();
			double tmp[dim];
			point c(dim);
			
			auto A = a.data();
			auto B = b.data();
			auto C = c.data();

			malgo::vector_scale(A, dim, 1 - k, tmp);
			malgo::vector_scale(B, dim, k, C);
			malgo::vector_add(tmp, C, dim, C);
			return c;
		}
	}
}
#endif
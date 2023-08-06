#ifndef GXX_COORDINATES_CORRECTION_TABLE_H
#define GXX_COORDINATES_CORRECTION_TABLE_H

#include <gxx/geom/ncurve.h>
#include <gxx/print/stdprint.h>
#include <algorithm>

namespace gxx {
	namespace ngeom {
		template <typename T>
		class single_axis_correction_table {
		public:
			std::vector<T> coords;
			malgo::matrix<T> table;
			uint8_t base_axis;
		
		public:
			single_axis_correction_table(	
				uint8_t dim,
				uint8_t base, 
				const std::vector<T>& corcoords,
				const std::vector<uint8_t>& numcoords,
				const malgo::matrix<T>& cormatrix
			) : base_axis(base), coords(corcoords), table(corcoords.size(), dim) {

				for (int i = 0; i < numcoords.size(); ++i) {
					auto ax = numcoords[i];
					
					//Копируем столбцы в расширенную таблицу
                                        table.column_view(ax) = cormatrix.column_view(i);

					//gxx::println(ax);
					//gxx::println(cormatrix);
					//gxx::println(table);
				}

			}

                        single_axis_correction_table(){}
                        single_axis_correction_table(int base, int dim) : base_axis(dim), coords(0), table(0, dim) {}

			single_axis_correction_table(	
				uint8_t base, 
				const std::vector<T>& coords,
				const malgo::matrix<T>& table
			) : base_axis(base), coords(coords), table(table) {}
			
			point evaluate(double coord) {
				int dim = table.size2();
				int anum;
				auto lower = std::upper_bound(coords.begin(), coords.end(), coord);
				if (lower == coords.end()) { 
					anum = coords.size() - 2; 
				}
				else {
					anum = std::distance(coords.begin(), lower) - 1;
				}		

				int bnum = anum+1;
				point ret(dim);
				double bkoeff = (coord - coords[anum]) / (coords[bnum] - coords[anum]);
				double akoeff = 1 - bkoeff;

				double* A = table.data() + dim * anum;
				double* B = table.data() + dim * bnum;
				double* C = ret.data();

				double tmp[dim];

				malgo::vector_scale(A, dim, akoeff, tmp);
				malgo::vector_scale(B, dim, bkoeff, C);
				malgo::vector_add(C, tmp, dim, C);

				//exit(0);
				return ret;

			}

			multiline correction( const line& l ) {
                                if (coords.size() == 0) return multiline(l.a, l.b);
				int dim = table.size2();

				const auto& first_point = l.pnt1();
				const auto& last_point = l.pnt2();
				double cstart = l.pnt1()[base_axis];
				double cstop = l.pnt2()[base_axis];
				bool reversed = cstart > cstop;
	
				double low = reversed ? cstop : cstart;
				double high = reversed ? cstart : cstop;
		
				auto lower = std::lower_bound(coords.begin(), coords.end(), low);
				auto upper = std::upper_bound(coords.begin(), coords.end(), high);

				std::vector<double> midcoord(lower, upper);
				auto distance = std::distance(lower, upper);
				auto inidx = std::distance(coords.begin(), lower);

				multiline ml(distance + 2, l.dim());
				malgo::vector_copy(first_point.data(), dim, ml.point_data(0));
				malgo::vector_copy(last_point.data(), dim, ml.point_data(ml.size() - 1));

				int i = 1;
				for (double& m : midcoord) {
					point p = l.points_with(base_axis, m)[0];
					malgo::vector_copy(p.data(), dim, ml.point_data(i++));
				}

				for (int i = 0; i < ml.size(); ++i) {
					point p = evaluate(ml.point_data(i)[base_axis]);
					malgo::vector_add(ml.point_data(i), p.data(), dim, ml.point_data(i));
				}
				return ml;
			}		

			template<typename R>
			void reflect(R& r) {
				r & base_axis;
				r & coords;
				r & table;
			}
		};


		
	}
}

#endif

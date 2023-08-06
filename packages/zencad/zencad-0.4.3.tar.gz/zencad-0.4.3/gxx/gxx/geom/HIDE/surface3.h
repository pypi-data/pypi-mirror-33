#ifndef GXX_SURFACE_H
#define GXX_SURFACE_H

namespace gxx {
	namespace surf3 {
		using namespace geom3;

		class surface {
		public:
			virtual point d0(double v, double u) = 0; 
			virtual bool is_v_closed() { return false; }
			virtual bool is_v_periodic() { return false; }
			virtual bool is_u_closed() { return false; }
			virtual bool is_u_periodic() { return false; }
			virtual double vmin() { return 0; }
			virtual double vmax() { return 0; }
			virtual double umin() { return 0; }
			virtual double umax() { return 0; }
			virtual ~surface() {}
			virtual size_t printTo(gxx::io::ostream& o) const { return gxx::print("surface"); }
		};

		class cylinder : public surface {
		public:
			double r;
			double h;
			axis3 ax3;

			cylinder(double r, double h, const axis3& ax3) : r(r), h(h), ax3(ax3) {}

			point d0(double v, double u) {
				double c = r * cos(v);
				double s = r * sin(v);
				double w = h * u;
				return point(
					ax3.l.x + ax3.dx.x * c + ax3.dy.x * s + ax3.dz.x * w,
					ax3.l.y + ax3.dx.y * c + ax3.dy.y * s + ax3.dz.y * w,
					ax3.l.z + ax3.dx.z * c + ax3.dy.z * s + ax3.dz.z * w
				);
			}
		};

		class sphere : public surface {
		public:
			double r;
			axis3 ax3;

			sphere(double r, double h, const axis3& ax3) : r(r), ax3(ax3) {}

			point d0(double v, double u) override {
				double a = r * cos(v) * cos(u);
				double b = r * sin(v) * cos(u);
				double c = r * sin(u);
				return point(
					ax3.l.x + ax3.dx.x * a + ax3.dy.x * b + ax3.dz.x * c,
					ax3.l.y + ax3.dx.y * a + ax3.dy.y * b + ax3.dz.y * c,
					ax3.l.z + ax3.dx.z * a + ax3.dy.z * b + ax3.dz.z * c
				);
			}
		};

		class plane : public surface {
		public:
			axis2 ax2;

			ACCESSOR(pos, ax2);

			plane(const axis2& ax2) : ax2(ax2) {}

			point d0(double v, double u) override {
				return point(ax2.loc() + ax2.dirx().scale(v) + ax2.diry().scale(u));				
			} 
		};
	}
}

#endif
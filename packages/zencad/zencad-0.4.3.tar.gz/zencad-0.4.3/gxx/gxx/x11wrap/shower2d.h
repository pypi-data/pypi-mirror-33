#ifndef GXX_X11_2D_SHOWER
#define GXX_X11_2D_SHOWER

#include <X11/Xlib.h>
#include <gxx/geom/sgeom2.h>

namespace g2 = gxx::geom2;

namespace gxx {
	//static std::vector<gxx::sgeom2::line> polygones(const gxx::geom2::curve, int xmin, int xmax, int ymin, int ymax) {

	//}
	class drawer2d {
	public:
		std::vector<gxx::sgeom2::point<double>> points;
		std::vector<gxx::sgeom2::line<double>> lines;
		std::vector<gxx::sgeom2::arc<double>> arcs;	


		/*void add_point(gxx::geom2::point pnt) {
			points.emplace_back(pnt.x, pnt.y);
		}

		void add_point(gxx::sgeom2::point<double> pnt) {
			points.emplace_back(pnt);
		}
*/
		void add_line(double x1, double y1, double x2, double y2) {
			lines.emplace_back(x1, y1, x2, y2);
		}

		/*void add_line(malgo::vector2<double> pnt1, malgo::vector2<double> pnt2) {
			lines.emplace_back(pnt1.x, pnt1.y, pnt2.x, pnt2.y);
		}*/
/*
		void add_line(gxx::sgeom2::line<double> lin) {
			lines.emplace_back(lin);
		}

		void add_line(gxx::geom2::point pnt1, gxx::geom2::point pnt2) {
			lines.emplace_back(pnt1.x, pnt1.y, pnt2.x, pnt2.y);
		}

		void add_arc(double x, double y, double w, double h, double a1, double a2) {
			arcs.emplace_back(x,y,w,h,a1,a2);
		}

		void add_curve(const gxx::geom2::curve& crv) {
			crv.drawTo(*this);
		}*/

		/*void add_figure(const gxx::topo2::figure& fig) {
			for (auto & c : fig.conts) {
				for (auto & s : c.segs) {
					add_curve(*s.crv);
				}
			}
		}*/				
	};

	class shower2d : public drawer2d {
	public:

		int s;
		Display *d;
		Window w;

		unsigned int width = 500;
		unsigned int height = 500;
		unsigned int xcenter;
		unsigned int ycenter;

		double scale = 1;

		shower2d() { update_window(width, height); }
			
		void draw_point(const gxx::sgeom2::point<double>& pnt) {
			int x = scale * (+ pnt.x) + xcenter + 0.5;
			int y = scale * (- pnt.y) + ycenter + 0.5;
			
			XDrawLine(d, w, DefaultGC(d, s), x - 5, y - 5, x + 5, y + 5);
			XDrawLine(d, w, DefaultGC(d, s), x - 5, y + 5, x + 5, y - 5);
		}

		void draw_line(const gxx::sgeom2::line<double>& lin) {
			int x1 = scale * (+ lin.x1) + xcenter + 0.5;
			int y1 = scale * (- lin.y1) + ycenter + 0.5;
			int x2 = scale * (+ lin.x2) + xcenter + 0.5;
			int y2 = scale * (- lin.y2) + ycenter + 0.5;
			
			XDrawLine(d, w, DefaultGC(d, s), x1, y1, x2, y2);
		}

		void draw_arc(const gxx::sgeom2::arc<double>& arc) {
			int x = scale * (+ arc.x) + xcenter + 0.5;
			int y = scale * (- arc.y) + ycenter + 0.5;
			int we = scale * arc.w + 0.5;
			int he = scale * arc.h + 0.5;
			int a1 = arc.a1 * 64 + 0.5;
			int a2 = arc.a2 * 64 + 0.5;
		
			XDrawArc(d,w,DefaultGC(d,s),x,y,we,he,a1,a2);
		}

		void update_window(unsigned int w, unsigned int h) {
			width = w;
			height = h;
			xcenter = width / 2;
			ycenter = height / 2;
		}

		void exec() {
			XEvent e;
			update_window(width, height);

			//Соединиться с X сервером, если X сервер на удаленной машине
			//следует разрешить на машине, где запущен X Server 
			//удаленные соединения командой xhost+ (см. man xhost)
			
			if ((d = XOpenDisplay(getenv("DISPLAY"))) == NULL) {
				printf("Can't connect X server:%s\n", strerror(errno));
				exit(1);
			}

			s = XDefaultScreen(d);

			/* Создать окно */
			w = XCreateSimpleWindow(d, RootWindow(d, s), 10, 10, width, height, 1, 0xffffff, 0xffffff);

			/* На какие события будем реагировать */
			XSelectInput(d, w, KeyPressMask | StructureNotifyMask);

			//Вывести окно на экран
			XMapWindow(d, w);

			//Бесконечный цикл обработки событий
			while (1) {
				XNextEvent(d, &e);

				//Перерисовать окно */
				if (e.type == ConfigureNotify) {
					XConfigureEvent xce = e.xconfigure;
					update_window(xce.width, xce.height);	
				}


				//При нажатии кнопки-выход
				if (e.type == KeyPress) {
					XKeyEvent ke = e.xkey;
					gxx::println(ke.keycode);
					if (ke.type == KeyPress) {
						if (ke.keycode == 24) {
							scale *= 1.1;
						}
						if (ke.keycode == 25) {
							scale /= 1.1;
						}
						XClearWindow(d,w);
					}
				}

				for (auto& p : points) draw_point(p);
				for (auto& l : lines) draw_line(l);
				for (auto& a : arcs) draw_arc(a);
			}

			//Закрыть соединение с X сервером
			XCloseDisplay(d);

			return;
		}
	};
} 

#endif
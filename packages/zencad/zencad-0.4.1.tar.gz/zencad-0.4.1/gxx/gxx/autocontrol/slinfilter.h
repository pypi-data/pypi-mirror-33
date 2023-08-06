#ifndef GXX_AUTOCONTROL_SLINFILTER_H
#define GXX_AUTOCONTROL_SLINFILTER_H

#include <math.h>

namespace gxx {
	namespace autocontrol {
		class stepped_aperiodic_filter {
		public:
			double koeff = 0;
			double* output; 
			double* input; 

			stepped_aperiodic_filter(double* inp, double* out) : 
				input(inp), output(out) {}

			void iteration() {
				*output += (*input - *output) * koeff;
			}

			void set_params(double step_ms, double timeconst_ms) {
				koeff = exp(-step_ms / timeconst_ms);
				//dprln(koeff);
			}

			void set_koeff(double koeff) {
				this->koeff = koeff;
			}
		};

		class dynamic_aperiodic_filter {
		public:
			double timeconst = 0;
			double* output; 
			double* input; 

			void iteration(double step) {
				*output += (*input - *output) * (exp(-step / timeconst));
			}
		};
	}
}

#endif
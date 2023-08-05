#include "array_add.h"

int add_array_double(double *a, double *b, double *out, long N) {
	double *pa, *pb, *pout;
	double *pa_max = a + N; //*pb_max = pb + N, *pout_max = out + N;
	for (pa = a, pb = b, pout = out; pa < pa_max; pa++, pb++, pout++) {
		*pout = *pa + *pb;
	}
	return 0;
}

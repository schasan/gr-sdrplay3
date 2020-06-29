/* -*- c++ -*- */

#define MSZ_API

%include "gnuradio.i"           // the common stuff

//load generated python docstrings
%include "msz_swig_doc.i"

%{
#include "msz/abs_ff.h"
#include "msz/square_ff.h"
#include "msz/rsp1a.h"
#include "msz/cw.h"
%}

%include "msz/abs_ff.h"
GR_SWIG_BLOCK_MAGIC2(msz, abs_ff);
%include "msz/square_ff.h"
GR_SWIG_BLOCK_MAGIC2(msz, square_ff);
%include "msz/rsp1a.h"
GR_SWIG_BLOCK_MAGIC2(msz, rsp1a);
%include "msz/cw.h"
GR_SWIG_BLOCK_MAGIC2(msz, cw);

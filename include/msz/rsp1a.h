/* -*- c++ -*- */
/*
 * Copyright 2020 Mario Schulz.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_MSZ_RSP1A_H
#define INCLUDED_MSZ_RSP1A_H

#include <msz/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace msz {

    /*!
     * \brief <+description of block+>
     * \ingroup msz
     *
     */
    class MSZ_API rsp1a : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<rsp1a> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of msz::rsp1a.
       *
       * To avoid accidental use of raw pointers, msz::rsp1a's
       * constructor is in a private implementation
       * class. msz::rsp1a::make is the public interface for
       * creating new instances.
       */
      static sptr make(float frequency, long sample_rate, int gain);

      /*!
       * \brief Pass frequency parameter from GUI
       */
      virtual void set_frequency(float freq) = 0;

      /*!
       * \brief Pass gain parameter from GUI
       */
      virtual void set_gain(int gain) = 0;

      /*!
       * \brief Pass sample rate parameter from GUI
       */
      virtual void set_sample_rate(long sample_rate) = 0;
    };

  } // namespace msz
} // namespace gr

#endif /* INCLUDED_MSZ_RSP1A_H */


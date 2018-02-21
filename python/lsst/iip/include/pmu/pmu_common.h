// -*-Mode: C;-*-

#ifndef PMU_COMMON_H
#define PMU_COMMON_H


/* ---------------------------------------------------------------------- *//*!

  \file   pmu_common.h
  \brief  Utility methods common to dealing with the Performance Monitors
          Unit.
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_common.h $

  \par Credits:
       SLAC

  \verbatim
                               Copyright 2013
                                    by
                       The Board of Trustees of the
                    Leland Stanford Junior University.
                           All rights reserved.
  \endverbatim
                                                                          */
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *\
 * 
 * HISTORY
 * -------
 *
 * DATE     WHO WHAT
 * -------- --- ---------------------------------------------------------
 * 05.05.13 jjr Created
 *
\* ---------------------------------------------------------------------- */

#include <stdio.h>

#ifdef __cplusplus
extern "C"
{
#endif

extern unsigned int PmuSelect;

/* ---------------------------------------------------------------------- *//*!

  \brief  Extract the bit field defined by its right-justified shift and
          in-place mask
  \return The extracted value

  \param[in] reg    The register value to extract the field from
  \param[in] shift  The right-justified shift
  \param[in] mask   The in-place bit mask
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_extract (unsigned int   reg,
                                        unsigned int shift,
                                        unsigned int  mask)
{
    unsigned int value = (reg >> shift) & (mask >> shift);
    return value;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Inserts the bit field defined by its right-justified shift and
          in-place mask
  \return The extracted value

  \param[in] reg    The register to insert the field to
  \param[in] value  The value to insert
  \param[in] shift  The right-justified shift
  \param[in] mask   The in-place bit mask
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_insert (unsigned int   reg,
                                       unsigned int value,
                                       unsigned int shift,
                                       unsigned int  mask)
{
    reg &= ~mask;
    reg |= (value & (mask>>shift)) << shift;
    return reg;
}
/* ---------------------------------------------------------------------- */


#ifdef __cplusplus
}
#endif


#endif

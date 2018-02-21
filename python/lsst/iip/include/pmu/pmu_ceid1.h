// -*-Mode: C;-*-

#ifndef PMU_CEID1_H
#define PMU_CEID1_H


/* ---------------------------------------------------------------------- *//*!

  \file   pmu_ceid1.h
  \brief  Provides accesss/interface to the Performance Monitors Common 
          Event ID Register 1
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_ceid1.h $

  \par Credits:
       SLAC

  \verbatim
                               Copyright 2013
                                    by
                       The Board of Trustees of the
                    Leland Stanford Junior University.
                           All rights reserved.
  \endverbatim

  \par Common Event Identifiers
   The ARM architecture designates event identifiers 0 - 0x3F as the common
   event identifiers.  This are reserved for the specified events. When an 
   ARMv7 processor supports monitoring of an event that is assigned a number
   in this range, if possible it must use that number for the event. 
   Unassigned values are reserved and might be used for additional common
   events in future versions of the architecture.

   The PMCCEID1 register is a read-only register that identifies which of
   the common event identifiers in the range 0x20-0x3F are actually
   implemented. This value is returned as a 32-bit mask. 

  \par Cavaet
   Currently no common events identifiers in the range 0x20 - 0x3F have
   been defined. Consequently, this register always reads 0. 
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


#ifdef __cplusplus
extern "C"
{
#endif


/* ---------------------------------------------------------------------- */
/* REGISTER ACCESS: Performance Monitor EID0 and CEID1 Register            */
/* ---------------------------------------------------------------------- */

static unsigned int pmu_ceid1_read ();

/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Primitive to read PMCEID1, the Performance Monitor Event 
          Identification register 1.

  \return The value of the Performance Monitor Event Identification 
          register 1

   The contents of the PMCCEID1  are not currently documented in the ARM
   architecture.

  \warning
   This is only provided for completeness. On the ZYNQ version of the
   ARM, this register appears not to be implemented.  It always returns 0.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_ceid1_read ()
{
    unsigned int reg;
    asm volatile (" MRC     p15, 0, %0, c9, c12, 7" : "=r"(reg) ::);
    return reg;
}
/* ---------------------------------------------------------------------- */

#ifdef __cplusplus
}
#endif

#endif

// -*-Mode: C;-*-

#ifndef PMU_SWINC_H
#define PMU_SWINC_H

/* ---------------------------------------------------------------------- *//*!

  \file   pmu_swinc.h
  \brief  Provides access/interface to the Performance Monitor Software
          Increment Register
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
      \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_swinc.h $

  \par Credits:
        SLAC

  \verbatim
                               Copyright 2013
                                    by
                       The Board of Trustees of the
                    Leland Stanford Junior University.
                           All rights reserved.
  \endverbatim

  \par Purpose
   The PMSWINC register increments the event counters that are configured
   to count the Software Increment event 0x00.

   \verbatim

   |31|30         N | N-1                                       0|
   +--+-----------------+----------------------------------------+
   | C| Reserved WI | Event counter software inscrement bits, Px |
   +--+-----------------+----------------------------------------+

   \endverbatim

    where
       -Px  Event count x, PMNx, softwware increment bit. This bit is
            write-only. The effects of writing to to this bit are
               - 0  No action, the write is ignored.
               - 1  If PMNx is enabled and configured to count the 
                    Software increment event
                      - Increment the the PMNx event counter by 1
               - 1  If PMNx is disabled or not configured to count
                    the Software increment event
                      - No, action, the write is ignored.

   \note
    Contrast the software event counter with other counters. These other
    counters are a tied to counting the number of occurances of a specific
    event, such as the number of instructions. Here, any number of 
    software counters (of course up to the limit N, the number of event
    counters) can be configured to count the software increment. This 
    allows the software to define up to N such counters to count 
    different aspects in the software.

    This feature is likely of more interest when the Performance Counting
    is performed remoted. In this case, the remote counter does not need
    to have any intimate knowledge of what is being counted.  On the 
    processor side, a simple memory location could be devoted to handle
    the counting.

   \note
    Since this is a write only register with only one defined writeable
    field and a reserved field that is ignored on write, the usual get
    and \set routines are not provided. 
                                                                          */
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *\
 * 
 * HISTORY
 * -------
 *
 * DATE     WHO WHAT
 * -------- --- ---------------------------------------------------------
 * 05.08.13 jjr Created
 *
\* ---------------------------------------------------------------------- */


#include  "pmu/pmu_common.h"


#ifdef __cplusplus
extern "C"
{
#endif


/* ---------------------------------------------------------------------- */
/* REGISTER ACCESS: Performance Monitor Control Register                  */
/* ---------------------------------------------------------------------- */

static void pmu_swinc_write (unsigned int  pmnxs);

/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \enum   _PMU_SWINC_S
  \brief   Maps out the sizes of the Performance Monitor SWINC fields
                                                                          *//*!
  \typedef PMU_PMNXS_S
  \brief   Typedef for enum _PMU_WSINC_S.

   This mapping is almost identical to the PMXS fields. The exception
   is this register only includes the event counters and not the Cycle
   Counter. Thus it consists of
         - An implementation dependent field giving the bit field of 
           event counters. This implementation defines the width as 6,
           the number of event counters in the zynq
         - An implementation dependent field giving the bit field of
           reserved bits. This bits are ignored on write.
 
 \note
  This is a write-only register
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_SWINC_S
{
    PMU_SWINC_S_PX   =  6, /*!< Size of the event counter field           */
    PMU_SWINC_S_RSVD = 26, /*!< Size of the reserved field.
                                This field is ignored on writes           */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_SWINC_S_TD
#define       PMU_SWINC_S_TD
typedef enum _PMU_SWINC_S    PMU_SWINC_S;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum   _PMU_SWINC_V
  \brief   Maps out the right-justified shift for each of the Performance
           Monitor PMSWINC fields
                                                                          *//*!
  \typedef PMU_SWINC_V
  \brief   Typedef for enum _PMU_SWINC_V.

   This mapping is almost identical to the PMXS fields. The exception
   is this register only includes the event counters and not the Cycle
   Counter. Thus it consists of
         - An implementation dependent field giving the bit field of 
           event counters. This implementation defines the width as 6,
           the number of event counters in the zynq
         - An implementation dependent field giving the bit field of
           reserved bits. This bits are ignored on write.
 
 \note
  This is a write-only register
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_SWINC_V
{
    PMU_SWINC_V_PX   =  0, /*!< Right shift of the event counter field    */
    PMU_SWINC_V_RSVD =  6, /*!< Right shift of the reserved field.
                                This field is ignored on writes.          */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_SWINC_V_TD
#define       PMU_SWINC_V_TD
typedef enum _PMU_SWINC_V    PMU_SWINC_V;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum   _PMU_SWINC_M
  \brief   Maps out the in place masks for each of the Performance Monitor
           PMSWINC fields
                                                                          *//*!
  \typedef PMU_SWINC_M
  \brief   Typedef for enum _PMU_SWINC_M

   This mapping is almost identical to the PMXS fields. The exception
   is this register only includes the event counters and not the Cycle
   Counter. Thus it consists of
         - An implementation dependent field giving the bit field of 
           event counters. This implementation defines the width as 6,
           the number of event counters in the zynq
         - An implementation dependent field giving the bit field of
           reserved bits. This bits are ignored on write.
 
 \note
  This is a write-only register
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_SWINC_M
{
    PMU_SWINC_M_PX   =  0x0000003F, /*< In place mask of the event 
                                        counter field                     */
    PMU_SWINC_M_RSVD =  0xFFFFFFC0, /*!< In place mask of the reserved
                                         field, this field reads as zero
                                         and is ignored on writes         */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_SWINC_M_TD
#define       PMU_SWINC_M_TD
typedef enum _PMU_SWINC_M    PMU_SWINC_M;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum    _PMU_USERENR_S
  \brief    Maps out the sizes of the bit fields in the Performance
            Monitor User Enable Register, PMUSERENR
                                                                          *//*!
  \typedef  PMU_USERENR_S
  \brief    Typedef for enum _PMU_USERENR_S
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_USERENR_S
{
    PMU_USERENR_S_ENABLE =  1, /*!< The size of the enable field          */
    PMU_USERENR_S_RSVD   = 31 /*!< Reserved UNK/SBZP                      */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_USERENR_S_TD
#define       PMU_USERENR_S_TD
typedef enum _PMU_USERENR_S PMU_USERENR_S;
#endif
/* ---------------------------------------------------------------------- */





/* ---------------------------------------------------------------------- *//*!

  \brief      Primitive to write PMSWINC, the Performance Monitor Software
              Increment register.

  \param[in]  pmnxs  The set of event counters to do a software increment
                     on

   The \a pmnxs represent a bit mask of event counters to be incremented.
   Because bits corresponding to unimplemented event counters are ignored
   no masking to the implementation limit of event counters is performed.

  \note
   Also note that only event counters configured to count the Software
   Increment event, \i.e. event 0, will be incremented.  While typically
   this would not be done, one is allowed to specify \a pmnxs = 0xffffffff
   to increment all such counters.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_swinc_write (unsigned int pmnxs)
{
    asm volatile (" MCR     p15, 0, %0, c9, c12, 4" : : "r"(pmnxs) :);
}
/* ---------------------------------------------------------------------- */


#ifdef __cplusplus
}
#endif

#endif

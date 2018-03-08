// -*-Mode: C;-*-

#ifndef PMU_PMNXS_H
#define PMU_PMNXS_H

/* ---------------------------------------------------------------------- *//*!

  \file   pmu_pmnxs.h
  \brief  
  \author JJRussell - russell@slac.stanford.edu

  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_pmnxs.h $

  \par Credits:
       SLAC

  \verbatim
                               Copyright 2013
                                    by
                       The Board of Trustees of the
                    Leland Stanford Junior University.
                           All rights reserved.
  \endverbatim


  \Purpose
   This defines the layout for the fields used by a number of register. 
   Thus, it is not ifself an actual register. 

  \Layout

  \verbatim

   |31|30             N | N-1                        |
   +--+-----------------+----------------------------+
   | C| Reserved RAZ/WI | Event Counter Disable Bits |
   +--+-----------------+----------------------------+

  \endverbatim

   where \e N is the number of counters in the implemented version of the
   Performance Monitor Unit.  On the Znyq, N = 6 counters.  

   \e C = enable/disable bit for the PMCCNTR


  \note
   In general, bits >= N will read 0. 

  \note
   Since the reserved field is always read as zero and ignored on write,
   no access methods are provided to this field.
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


#include  "pmu/pmu_common.h"

#ifdef __cplusplus
extern "C" {
#endif


/* ---------------------------------------------------------------------- *//*!

  \enum   _PMU_PMNXS_S
  \brief   Maps out the sizes of the Performance Monitor PMNXs fields
                                                                          *//*!
  \typedef PMU_PMNXS_S
  \brief   Typedef for enum _PMU_PMNXS_S.

   The PMNXS is 32-bit unsigned integer used in a number of PMU register 
   reads and writes.  It consists for 3 fields which are, from least
   significant bit to most significant bits
         - An implementation dependent field giving the bit field of 
           event counters. This implementation defines the width as 6,
           the number of event counters in the zynq
         - An implementation dependent field giving the bit field of
           reserved bits. This bits are read as zeros and ignored on
           write.
         - A one bit field identifying the PMCCNTR, the cycle counter
           register.
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_PMNXS_S
{
    PMU_PMNXS_S_PXS  =  6, /*!< Size of the event counters field          */
    PMU_PMNXS_S_RSVD = 25, /*!< Size of the reserved field, this field 
                                 reads as zero and is ignored on writes   */
    PMU_PMNXS_S_C    =  1  /*!< Size the PMCCNTR select bit               */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_PMNXS_S_TD
#define       PMU_PMNXS_S_TD
typedef enum _PMU_PMNXS_S    PMU_PMNXS_S;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum   _PMU_PMNXS_V
  \brief   Maps out the right-justified shift for each of the Performance
           Monitor PMNXs fields
                                                                          *//*!
  \typedef PMU_PMNXS_V
  \brief   Typedef for enum _PMU_PMNXS_V.

   The PMNXS is 32-bit unsigned integer used in a number of PMU register 
   reads and writes.  It consists for 3 fields which are, from least
   significant bit to most significant bits
         - An implementation dependent field giving the bit field of 
           event counters. This implementation defines the width as 6,
           the number of event counters in the zynq
         - An implementation dependent field giving the bit field of
           reserved bits. This bits are read as zeros and ignored on
           write.
         - A one bit field identifying the PMCCNTR, the cycle counter
           register.
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_PMNXS_V
{
    PMU_PMNXS_V_PXS  =  0, /*!< Right shift of the event counter field    */
    PMU_PMNXS_V_RSVD =  6, /*!< Right shift of the reserved field, this
                                field reads as zero and is ignored on
                                writes                                    */
    PMU_PMNXS_V_C    = 31  /*!< Right shift of the PMCCNTR select bit     */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_PMNXS_V_TD
#define       PMU_PMNXS_V_TD
typedef enum _PMU_PMNXS_V    PMU_PMNXS_V;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum   _PMU_PMNXS_M
  \brief   Maps out the in place masks for each of the Performance Monitor
           PMNXs fields
                                                                          *//*!
  \typedef PMU_PMNXS_M
  \brief   Typedef for enum _PMU_PMNXS_M

   The PMNXS is 32-bit unsigned integer used in a number of PMU register 
   reads and writes.  It consists for 3 fields which are, from least
   significant bit to most significant bits
         - An implementation dependent field giving the bit field of 
           event counters. This implementation defines the width as 6,
           the number of event counters in the zynq
         - An implementation dependent field giving the bit field of
           reserved bits. This bits are read as zeros and ignored on
           write.
         - A one bit field identifying the PMCCNTR, the cycle counter
           register.
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_PMNXS_M
{
    PMU_PMNXS_M_PXS  =  0x0000003F, /*< In place mask of the event 
                                        counter field                     */
    PMU_PMNXS_M_RSVD =  0x7FFFFFC0, /*!< In place mask of the reserved
                                         field, this field reads as zero
                                         and is ignored on writes         */
    PMU_PMNXS_M_C    =  0x80000000, /*!< In place mask of the PMCCNTR 
                                         select bit                       */
    PMU_PMNXS_M_ALL  =  0xffffffff  /*!< Target all counters              */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_PMNXS_M_TD
#define       PMU_PMNXS_M_TD
typedef enum _PMU_PMNXS_M    PMU_PMNXS_M;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- */
/* FIELD ACCESS: Provides access, both read and write to the fields of    */
/*               of registers that return this layout.                    */
/* ---------------------------------------------------------------------- */

static inline unsigned int pmu_pmnxs_pxs_get  (unsigned int pmnxs);
static inline unsigned int pmu_pmnxs_c_get    (unsigned int pmnxs);

static inline unsigned int pmu_pmnxs_pxs_set  (unsigned int pmnxs,
                                               unsigned int   pxs);
static inline unsigned int pmu_pmnxs_c_set    (unsigned int pmnxs,
                                               unsigned int     c);

/* ---------------------------------------------------------------------- */






/* ---------------------------------------------------------------------- *//*!

  \brief  Returns a bit mask corresponding to the event counters.
  \return A bit mask corresponding to the event counters, but not
          the Cycle Counter.

  \param[in] pmnxs The value of the register formatted as a PMNXS register
                                                                          */
/* ---------------------------------------------------------------------- */
static unsigned int pmu_pmnxs_pxs_get  (unsigned int pmnxs)
{
    unsigned int pxs = pmu_extract (pmnxs, PMU_PMNXS_V_PXS, PMU_PMNXS_M_PXS);
    return pxs;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Returns a flag corresponding to the Cycle Counter.
  \return A bit mask corresponding to the Cycle Counter.

  \param[in] pmnxs The value of the register formatted as a PMNXS register
                                                                          */
/* ---------------------------------------------------------------------- */
static unsigned int pmu_pmnxs_c_get (unsigned int pmnxs)
{
    unsigned int c = pmu_extract (pmnxs, PMU_PMNXS_V_C, PMU_PMNXS_M_C);
    return c;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the PXs event counters mask. This does not
          include the Cycle Counter
  \return The new value of PXs event counters mask.

  \param[in] pmnxs The value of the register formatted as a PMNXS register
  \param[in] pxs   The new value of bit mask of PXS event counters.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_pmnxs_pxs_set  (unsigned int pmnxs,
                                               unsigned int   pxs)
{
    pmnxs = pmu_insert (pmnxs, pxs, PMU_PMNXS_V_PXS, PMU_PMNXS_M_PXS);
    return pmnxs;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the Cycle Counter bit.
  \return The new value of PXs event counters mask.

  \param[in] pmnxs The value of the register formatted as a PMNXS register
  \param[in] c     The new state of the Cycle Counter bit
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_pmnxs_c_set (unsigned int pmnxs,
                                            unsigned int     c)
{
    pmnxs = pmu_insert (pmnxs, c, PMU_PMNXS_V_C, PMU_PMNXS_M_C);
    return pmnxs;
}
/* ---------------------------------------------------------------------- */

#ifdef __cplusplus
}
#endif

#endif

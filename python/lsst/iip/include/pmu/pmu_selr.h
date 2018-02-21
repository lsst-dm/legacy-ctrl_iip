// -*-Mode: C;-*-

#ifndef PMU_SELR_H
#define PMU_SELR_H


/* ---------------------------------------------------------------------- *//*!

  \file   pmu_selr.h
  \brief  Provides access/interface t the Performance Monitor Event
          Counter Selection Register.
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
     \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_selr.h $

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

   PMSLR selects an event counter, PMNx, or the cycle counter, CCNT.
   The PMSELR.SEL value of 31 selects the cycle counter.

  \par Layout

  \verbatim

   |31              5 | 4  0|
   +------------------+-----+
   | RSVD, UNK/SBZP   | SEL |
   +--+---------------+-----+

  \endverbatim

   where
     - SEL  Selects event counter, PMNx, where x is tha value held in this
            field. That is the SEL filed identifies which event counter,
            PMNx, is accessed whwn a subseqent access to PMXEVTVER or
            PMXEVTCNtR occurs.  This field can take any value from 0 to
            to N -1 (the number of counters - 1), or 31. When PMSELR.SEL
            is 31 it
               - Selects the PMXEVTYPER for the cycle counter
               - A read or write of PMXEVCNTR is unpredicable
            If this field is set to a value greater than or equal to the
            number of implemented counters (N), but not equal to 31, the
            results are unpredicable.
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
/* REGISTER ACCESS: Performance Monitor Event Selection Register          */
/* ---------------------------------------------------------------------- */

static unsigned int pmu_selr_read     ();
static void         pmu_selr_write    (unsigned int selr);

static unsigned int pmu_selr_sel_get  (unsigned int selr);
static unsigned int pmu_selr_rsvd_get (unsigned int selr);

static unsigned int pmu_selr_sel_set  (unsigned int selr, 
                                       unsigned int pmnx);
static unsigned int pmu_selr_rsvd_set (unsigned int selr,
                                       unsigned int rsvd);

/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum    _PMU_SELR_S
  \brief    Maps out the sizes of the bit fields in the Performance
            Monitor Control Selection Register, PMSELR.
                                                                          *//*!
  \typedef  PMU_SELR_S
  \brief    Typedef for enum _PMU_SELR_S
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_SELR_S
{
    PMU_SELR_S_SEL   = 5, /*!< The size of the event counter, PMNx,
                               selection field, where \e x is the value 
                               held in this field. When this value is 31,
                               the Cycle Counter is selected.             */
    PMU_SELR_S_RSVD = 27  /*!< Reservedm UNK/SBZP                         */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_SELR_S_TD
#define       PMU_SELR_S_TD
typedef enum _PMU_SELR_S PMU_SELR_S;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum    _PMU_SELR_V
  \brief    Maps out the right-justified shifts of the bit fields in the
            Performance Monitor Control Selection Register, PMSELR.
                                                                          *//*!
  \typedef  PMU_SELR_V
  \brief    Typedef for enum _PMU_SELR_V
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_SELR_V
{
    PMU_SELR_V_SEL  = 0,  /*!< The right-justified shift of the event
                               counter, PMNx, selection field, where \e x 
                               is the value held in this field. When this
                               value is 31, the Cycle Counter is selected.*/
    PMU_SELR_V_RSVD = 5,  /*!< Reservedm UNK/SBZP                         */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_SELR_V_TD
#define       PMU_SELR_V_TD
typedef enum _PMU_SELR_V PMU_SELR_V;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum    _PMU_SELR_M
  \brief    Maps out the in-place masks of the bit fields in the
            Performance Monitor Control Selection Register, PMSELR.
                                                                          *//*!
  \typedef  PMU_SELR_M
  \brief    Typedef for enum _PMU_SELR_M
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_SELR_M
{
    PMU_SELR_M_SEL   = 0x0000001F, /*!< The right-justified shift of the
                                        event counter, PMNx, selection 
                                        field, where \e x is the value 
                                        held in this field. When this
                                        value is 31, the Cycle Counter is
                                        selected.                         */
    PMU_SELR_M_RSVD = 0xFFFFFFE0,  /*!< Reservedm UNK/SBZP                */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_SELR_M_TD
#define       PMU_SELR_M_TD
typedef enum _PMU_SELR_M PMU_SELR_M;
#endif
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \brief  Primitive to read PMSELR, the Performance Monitor Event Counter
          Selection Register.
  \return The value of the Performance Monitor Event Counter Selection
          Register.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_selr_read ()
{
    unsigned int reg;
    asm volatile (" MRC     p15, 0, %0, c9, c12, 5" : "=r"(reg) : : "memory");
    return reg;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief      Primitive to write PMSELR, the Performance Monitor Event
              Counter Selection Register.

  \param[in]  pmnx  The event counter to select
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_selr_write (unsigned int pmnx)
{
    asm volatile (" MCR     p15, 0, %0, c9, c12, 5" :: "r"(pmnx) : "memory");
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief   Returns the currently selected event counter, pmnx
  \return  The currently selected event counter. This is value between
           0 - N-1, where N is the number of event counters. (N is
           6 in the V7.2 implementation,

  \param[in] selr The Performance Monitor Event Selection Register
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_selr_sel_get  (unsigned int selr)
{
    unsigned int pmnx = pmu_extract (selr, PMU_SELR_V_SEL, PMU_SELR_M_SEL);
    return pmnx;
}
/* ---------------------------------------------------------------------- */

    

/* ---------------------------------------------------------------------- *//*!

  \brief   Return the value of reserved field
  \return  The value of the reserved field

  \param[in] selr The Performance Monitor Event Selection Register

  \note
   This routine is provided only somewhat for completeness. This reserved
   field is catagorized as UNK/SBZP. Since it is 'should be zero, but
   perserve, a get routine has been provided to facilitate the
   preservation of this field.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_selr_rsvd_get (unsigned int selr)
{
    unsigned int rsvd = pmu_extract (selr, PMU_SELR_V_RSVD, PMU_SELR_M_RSVD);
    return rsvd;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the event counter, pmnx, to be selected
  \return The new value of the Performance Monitor Event Selection Register

  \param[in] selr  The Performance Monitor Event Selection Register
  \param[in] pmnx  The event counter to select. This is a value between
                   0 - N-1, where N is the number of event counters. For
                   V7.2 the number of counters is 6.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_selr_sel_set  (unsigned int selr,
                                              unsigned int pmnx)
{
    selr = pmu_insert (selr, pmnx, PMU_SELR_V_SEL, PMU_SELR_M_SEL);
    return selr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the value of the reserved field
  \return The new value of the Performance Monitor Event Selection Register
          reserved field.

  \param[in] selr  The Performance Monitor Event Selection Register
  \param[in] rsvd  The value of the reserved field

  \note
   This routine is provided only somewhat for completeness. This reserved
   field is catagorized as UNK/SBZP. Since it is 'should be zero, but
   perserve, a set routine has been provided to facilitate the
   preservation of this field.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_selr_rsvd_set (unsigned int selr,
                                              unsigned int rsvd)
{
    selr = pmu_insert (selr, rsvd, PMU_SELR_V_RSVD, PMU_SELR_M_RSVD);
    return selr;
}
/* ---------------------------------------------------------------------- */


#ifdef __cplusplus
}
#endif

#endif

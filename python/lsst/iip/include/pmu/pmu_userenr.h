// -*-Mode: C;-*-

#ifndef PMU_USERENR_H
#define PMU_USERENR_H

/* ---------------------------------------------------------------------- *//*!

  \file   pmu_userenr.h
  \brief  Provides access/interface to the Performance Monitor User
          Enable Register
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
      \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_userenr.h $

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
   PMUSERENR enables or disables User mode access to the Performance
   Monitors.

  \par Layout

  \verbatim

   |31                             1 0|
   +-------------------------------+--+
   |     Reserved, UNK/SBZP        |EN|
   +-------------------------------+--+

  \endverbatim

    where
       -EN Use mode access enable ibt. The possible value of this bit are:
            -0  User mode access to the Performance Monitors is disabled
            -1  User mode access to the Performance Monitors is enabled

  \note
    This bit accessible in:
         - all PL1 modes
         - User mode, as read-only
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
/* REGISTER ACCESS: Performance Monitor User Enable Register              */
/* ---------------------------------------------------------------------- */

static unsigned int pmu_userenr_read       ();
static void         pmu_userenr_write      (unsigned int userenr);

static unsigned int pmu_userenr_enable_get (unsigned int userenr);
static unsigned int pmu_userenr_rsvd_get   (unsigned int userenr);


static unsigned int pmu_userenr_enable_set (unsigned int userenr,
                                            unsigned int enable);
static unsigned int pmu_userenr_rsvd_set   (unsigned int userenr,
                                            unsigned int   rsvd);


/* ---------------------------------------------------------------------- *//*!

  \enum    _PMU_USERENR_V
  \brief    Maps out the right-justified shifts of the bit fields in the
            Performance Monitor User Enable Register, PMUSERENR.
                                                                          *//*!
  \typedef  PMU_USERENR_V
  \brief    Typedef for enum _PMU_USERENR_V
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_USERENR_V
{
    PMU_USERENR_V_ENABLE =  0, /*!< The right-justified shift of the 
                                    enable field                          */
    PMU_USERENR_V_RSVD   =  1  /*!< The right-justified shift of the
                                    Reserved UNK/SBZP field               */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_USERENR_V_TD
#define       PMU_USERENR_V_TD
typedef enum _PMU_USERENR_V PMU_USERENR_V;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum    _PMU_USERENR_M
  \brief    Maps out the in-place masks of the bit fields in the
            Performance Monitor User Enable Register, PMUSERENR.
                                                                          *//*!
  \typedef  PMU_USERENR_M
  \brief    Typedef for enum _PMU_USERENR_M
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_USERENR_M
{
    PMU_USERENR_M_ENABLE =  0x00000001, /*!< The in-place mask of the 
                                             enable field                 */
    PMU_USERENR_M_RSVD   =  0xFFFFFFFE  /*!< The in-place mask of the
                                             Reserved UNK/SBZP field      */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_USERENR_M_TD
#define       PMU_USERENR_M_TD
typedef enum _PMU_USERENR_M    PMU_USERENR_M;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Primitive to read PMUSERENR, the Performance Monitor User
          Enable Register.
  \return The value of the Performance Monitor User Enable Register.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_userenr_read ()
{
    unsigned int userenr;
    asm volatile (" MRC     p15, 0, %0, c9, c14, 0" : "=r"(userenr) ::);
    return userenr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief      Primitive to write PMUSERENR, the Performance Monitor User
              Enable Register.

  \param[in]  enable_flag  Flag to disable(0)/enable(1) the performance
                           monitor for use in user mode.
                                                                         */
/* ---------------------------------------------------------------------- */
static inline void pmu_userenr_write (unsigned int userenr)
{
    asm volatile (" MCR     p15, 0, %0, c9, c14, 0" : : "r"(userenr) :);
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief   Returns the User Access enable flag
  \retval  == 0  User Access is disabled
  \return  == 1  User Access is enabled

  \param[in] userenr The Performance Monitor User Access Register 
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_userenr_enable_get  (unsigned int userenr)
{
    unsigned int enb = pmu_extract (userenr, PMU_USERENR_V_ENABLE, 
                                             PMU_USERENR_M_ENABLE);
    return enb;
}
/* ---------------------------------------------------------------------- */

    

/* ---------------------------------------------------------------------- *//*!

  \brief   Return the value of reserved field
  \return  The value of the reserved field

  \param[in] userenr The Performance Monitor Event Selection Register

  \note
   This routine is provided only somewhat for completeness. This reserved
   field is catagorized as UNK/SBZP. Since it is 'should be zero, but
   perserve, a get routine has been provided to facilitate the
   preservation of this field.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_userenr_rsvd_get (unsigned int userenr)
{
    unsigned int rsvd = pmu_extract (userenr, PMU_USERENR_V_RSVD, 
                                              PMU_USERENR_M_RSVD);
    return rsvd;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of User Access enable bit.
  \return The new value of the Performance Monitor Event Selection Register

  \param[in] userenr  The Performance Monitor Event Selection Register
  \param[in] enable   The value of the enable bit 
                        - 0 User Access is disabled
                        - 1 User Access is enabled
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_userenr_enable_set  (unsigned int userenr,
                                                    unsigned int  enable)
{
    userenr = pmu_insert (userenr, enable, PMU_USERENR_V_ENABLE,
                                           PMU_USERENR_M_ENABLE);
    return userenr;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the value of the reserved field
  \return The new value of the Performance Monitor User Access Register

  \param[in] userenr  The Performance Monitor Event Selection Register
  \param[in] rsvd     The value of the reserved field

  \note
   This routine is provided only somewhat for completeness. This reserved
   field is catagorized as UNK/SBZP. Since it is 'should be zero, but
   perserve, a set routine has been provided to facilitate the
   preservation of this field.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_userenr_rsvd_set (unsigned int userenr,
                                                 unsigned int    rsvd)
{
    userenr = pmu_insert (userenr, rsvd, PMU_USERENR_V_RSVD, 
                                         PMU_USERENR_M_RSVD);
    return userenr;
}
/* ---------------------------------------------------------------------- */



#ifdef __cplusplus
}
#endif


#endif

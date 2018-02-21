// -*-Mode: C;-*-

#ifndef PMU_XEVTYPER_H
#define PMU_XEVTYPER_H

/* ---------------------------------------------------------------------- *//*!

  \file   pmu_evttyper.h
  \brief  Provides access/interface to the Performance Monitors Event
          Type Select Register
           Register
  \author JJRussell - russell@slac.stanford.edu
   

  \par Last commit:
      \$Date: 2015-02-04 10:32:38 -0800 (Wed, 04 Feb 2015) $ by \$Author: wittgen $.

  \par Revision number
     \$Revision: 19237 $

  \par Location in repository:
     \$HeadURL: svn+ssh://jrussell@svn.cern.ch/reps/muondaq/CSCNRC/trunk/pmu/inc/pmu_xevtyper.h $

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
   When PMSELR.SEL selects an event counter, PMNx, PMXEVTYPER configures
   which event identifier increments that event counter. If 
   PMSELR.SEL = 31, then PMCCNTR is selected.  See the enumeration
   \sa PMU_EID_K for the definitions of the event identifiers.

   \verbatim

   |31|30|29                  8|7        0|
   +-=+--+--------------------+----------+
   | P| U| Reserved, UNK/SBZP | evtCount |
   +--+--+--------------------+----------+

   \endverbatim

   where:
       - P Priviledged execution filtering bit. Controls counting when
           execution is at PL1. The possible values of this bit are:
             - 0 Counts events when executing at PL1
             - 1 Do no count events when executing at PL1

       -U Unpriviledged execution filtering bit. Controls counting when
          execution is a PL0. The possible values of this bit are:
             - 0 Counts events when executing at PL0
             - 1 Do no count events when executing at PL0
 
       - evtCount Event to count. The event number of the event that is 
         counted by the selected event counter, PMNx. 
         See \sa enum PMU_EID_K for the list of event that can be counted.
         This field is reserved when PMSELR.SEL is set to 31 to select
         PMCCNTR.

   \note PMXEVTYPER reset values
    Immmediately after a non-debug logic reset
      - The values of the instances of PMXEVTYPER that relate to a event
        counter are \e UNKNOWN. That is, if m is one less than the number
        of implemented event counters, the non-debug reset values of
        PMXEVTYPER0 - PMXEVTYPERm are \e UNKNOWN
      - The reset values of the defined fields of the instance of 
        PMXEVTYPER that relates to the cycle counter are zero. That is,
        the non-debug reset value of PMXEVTYPER31.{P,U} is {0, 0}.
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

static unsigned int pmu_xevtyper_read  ();
static void         pmu_xevtyper_write (unsigned int xevtyper);


static unsigned int pmu_xevtyper_get_eid  (unsigned int xevtyper);
static unsigned int pmu_xevtyper_get_rsvd (unsigned int xevtyper);
static unsigned int pmu_xevtyper_get_u    (unsigned int xevtyper);
static unsigned int pmu_xevtyper_get_p    (unsigned int xevtyper);
static unsigned int pmu_xevtyper_get_pu   (unsigned int xevtyper);


static unsigned int pmu_xevtyper_set_eid  (unsigned int xevtyper,
                                           unsigned int     eid);
static unsigned int pmu_xevtyper_set_rsvd (unsigned int xevtyper,
                                           unsigned int     rsvd);
static unsigned int pmu_xevtyper_set_u    (unsigned int xevtyper,
                                           unsigned int        u);
static unsigned int pmu_xevtyper_set_p    (unsigned int xevtyper,
                                           unsigned int        p);
static unsigned int pmu_xevtyper_set_pu   (unsigned int xevtyper,
                                           unsigned int       pu);

/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum    _PMU_XEVTYPER_S
  \brief    Maps out the sizes of the bit fields in the Performance
            Monitor Event Type Select Register, PMXEVTYPER
                                                                          *//*!
  \typedef  PMU_XEVTYPER_S
  \brief    Typedef for enum _PMU_XEVTYPER_S

   This selects which event to count. The events are selected from the
   enumeration \sa PMU_EID_K.
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_XEVTYPER_S
{
    PMU_XEVTYPER_S_EID     =  8, /*!< The size of the event to count field*/
    PMU_XEVTYPER_S_RSVD    = 22, /*!< The size of the Reserved UNK/SBZP
                                      field                               */
    PMU_XEVTYPER_S_U       =  1, /*!< The size of the unprivileged filter
                                      flag                                */
    PMU_XEVTYPER_S_P       =  1, /*!< The size of the privileged filter 
                                      flag                                */
    PMU_XEVTYPER_S_PU      =  2, /*!< The size of the privileded and  
                                       unprivileged filter flags           */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_XEVTYPER_S_TD
#define       PMU_XEVTYPER_S_TD
typedef enum _PMU_XEVTYPER_S    PMU_XEVTYPER_S;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum    _PMU_XEVTYPER_V
  \brief    Maps out the right-justified shifts of the bit fields in the
            Performance Monitor Event Type Select Register, PMXEVTYPER.
                                                                          *//*!
  \typedef  PMU_XEVTYPER_V
  \brief    Typedef for enum _PMU_XEVTYPER_V

   This selects which event to count. The events are selected from the
   enumeration \sa PMU_EID_K.
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_XEVTYPER_V
{
    PMU_XEVTYPER_V_EID     =  0, /*!< The right-justified shift of the 
                                      event to count field                */
    PMU_XEVTYPER_V_RSVD    =  8, /*!< The right-justified shift of the
                                      Reserved UNK/SBZP field             */
    PMU_XEVTYPER_V_U       = 30, /*!< The right-justified shift of the
                                      unprivileged filter flag            */
    PMU_XEVTYPER_V_P       = 31, /*!< The right-justified shift of the
                                      privileged filter flag              */
    PMU_XEVTYPER_V_PU      =  2, /*!< The right-justified shift of the
                                      privileded and unprivileged filter
                                      flags                               */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_XEVTYPER_V_TD
#define       PMU_XEVTYPER_V_TD
typedef enum _PMU_XEVTYPER_V    PMU_XEVTYPER_V;
#endif
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \enum    _PMU_XEVTYPER_M
  \brief    Maps out the in-place masks of the bit fields in the
            Performance Monitor Event Type Select Register, PMXEVTYPER.
                                                                          *//*!
  \typedef  PMU_XEVTYPER_M
  \brief    Typedef for enum _PMU_XEVTYPER_M

   This selects which event to count. The events are selected from the
   enumeration \sa PMU_EID_K.
                                                                          */
/* ---------------------------------------------------------------------- */
enum _PMU_XEVTYPER_M
{
    PMU_XEVTYPER_M_EID     =  0x000000FF, /*!< The in-place mask of the 
                                               event to count field       */
    PMU_XEVTYPER_M_RSVD    =  0x3FFFFF00, /*!< The in-place mask of the
                                               Reserved UNK/SBZP field    */
    PMU_XEVTYPER_M_U       =  0x40000000, /*!< The in-place mask of the
                                               unprivileged filter flag   */
    PMU_XEVTYPER_M_P       =  0x80000000, /*!< The in-place mask of the
                                               privileged filter flag     */
    PMU_XEVTYPER_M_PU      =  0xC0000000, /*!< The in-place mask of the
                                               privileded and 
                                               unprivileged filter flags  */
};
/* ---------------------------------------------------------------------- */
#ifndef       PMU_XEVTYPER_M_TD
#define       PMU_XEVTYPER_M_TD
typedef enum _PMU_XEVTYPER_M    PMU_XEVTYPER_M;
#endif
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \brief  Primitive to read PMXEVTYPER, the Performance Monitor Event
          Type Select Register.
  \return The value of the Performance Monitor Event Type Select Register.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_xevtyper_read ()
{
    unsigned int reg;
    asm volatile (" MRC     p15, 0, %0, c9, c13, 1" : "=r"(reg) :: "memory");
    return reg;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Primitive to write PMXEVTYPER, the Performance Monitor Event
          Type Select Register.

  \param[in] xevttyper The value to write
                                                                          */
/* ---------------------------------------------------------------------- */
static inline void pmu_xevtyper_write (unsigned int xevtyper)
{
    asm volatile (" MCR     p15, 0, %0, c9, c13, 1" : : "r"(xevtyper) : "memory");
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Return the event type identifier 
  \return The event type identifier 

  \param[in] xevtyper  The Performance Monitor Event Type Select Register
                       value.
                                                                         */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_xevtyper_get_eid  (unsigned int xevtyper)
{
    unsigned int eid = pmu_extract (xevtyper, PMU_XEVTYPER_V_EID,
                                              PMU_XEVTYPER_M_EID);
    return eid;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief   Return the value of reserved field
  \return  The value of the reserved field

  \param[in] xevtypver The Performance Monitor Event Type Select Register 
                       value

  \note
   This routine is provided only somewhat for completeness. This reserved
   field is catagorized as UNK/SBZP. Since it is 'should be zero, but
   perserve, a get routine has been provided to facilitate the
   preservation of this field.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_xevtyper_get_rsvd (unsigned int xevtyper)
{
    unsigned int rsvd = pmu_extract (xevtyper, PMU_XEVTYPER_V_RSVD,
                                               PMU_XEVTYPER_M_RSVD);
    return rsvd;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \brief  Return the value of unprivileged execution filtering bit.
  \return The value of unprivileged execution filtering bit.

  \param[in] xevtyper  The Performance Monitor Event Type Select Register
                       value.

   This bit countrols counting when execution is at PL0. If this bit is
   set, then no counting of events occurs at PL0.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_xevtyper_get_u (unsigned int xevtyper)
{
    unsigned int u = pmu_extract (xevtyper, PMU_XEVTYPER_V_U,
                                            PMU_XEVTYPER_M_U);
    return u;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \brief  Return the value of privileged execution filtering bit.
  \return The value of privileged execution filtering bit.

  \param[in] xevtyper  The Performance Monitor Event Type Select Register
                       value.

   This bit countrols counting when execution is at PL1. If this bit is
   set, then no counting of events occurs at PL1.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_xevtyper_get_p (unsigned int xevtyper)
{
    unsigned int p = pmu_extract (xevtyper, PMU_XEVTYPER_V_P,
                                            PMU_XEVTYPER_M_P);
    return p;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Return the value of unprivileged and privileged execution 
          filtering bits.
  \retval == 0 No filtering performed.
  \retval == 1 Unprivileged execution filtering performed
  \retval == 2 Privileged execution filtering performed
  \retval == 3 Both unprivileged and privileged execution performed        

  \param[in] xevtyper  The Performance Monitor Event Type Select Register
                       value.

   These bit countrol counting when execution is at PL0 and/or PL1. If
   the corresponding bit is set, then do not event count events at that
   level.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_xevtyper_get_pu (unsigned int xevtyper)
{
    unsigned int pu = pmu_extract (xevtyper, PMU_XEVTYPER_V_PU,
                                             PMU_XEVTYPER_M_PU);
    return pu;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief Sets the value of the event type identifier.  This is typically
         used in conjunction with the Performance Monitors Event Selection
         Register to associate an event to count with a counter.
  
 \param[in]  xevtyper  The Performance Montitor Event Type Select 
                       register value.

 \param[in]      eid   The event type identifier to set. This is a value
                       from the enumeration \sa PMU_EID_K.
                                                                          */
/* ---------------------------------------------------------------------- */  
static inline unsigned int pmu_xevtyper_set_eid  (unsigned int xevtyper,
                                                  unsigned int      eid)
{
    xevtyper = pmu_insert (xevtyper, eid, PMU_XEVTYPER_V_EID,
                                          PMU_XEVTYPER_M_EID);
    return xevtyper;
}
/* ---------------------------------------------------------------------- */
   


/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the value of the reserved field
  \return The new value of the Performance Monitor Event Type Select Register

  \param[in] xevtyper  The Performance Monitor Event Type Select Register
                       value
  \param[in] rsvd      The value of the reserved field

  \note
   This routine is provided only somewhat for completeness. This reserved
   field is catagorized as UNK/SBZP. Since it is 'should be zero, but
   perserve, a set routine has been provided to facilitate the
   preservation of this field.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_xevtyper_set_rsvd (unsigned int xevtyper,
                                                  unsigned int     rsvd)
{
    xevtyper = pmu_insert (xevtyper, rsvd, PMU_XEVTYPER_V_RSVD,
                                           PMU_XEVTYPER_M_RSVD);
    return xevtyper;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the Performance Monitor Event Type Register
          unprivileged execution filtering bit.
  \return The new value of the Performance Monitor Event Type Select 
          Register

  \param[in] xevtyper  The Performance Monitor Event Type Select Register
                       value
  \param[in] u         The value of the unprivileged execution filtering
                       bit
                          -0 Count events when executing at PL0.
                          -1 Do not count events when executing at PL0.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_xevtyper_set_u (unsigned int xevtyper,
                                               unsigned int        u)
{
    xevtyper = pmu_insert (xevtyper, u, PMU_XEVTYPER_V_U,
                                        PMU_XEVTYPER_M_U);
    return xevtyper;
}
/* ---------------------------------------------------------------------- */



/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the Performance Monitor Event Type Register
          privileged execution filtering bit.
  \return The new value of the Performance Monitor Event Type Select 
          Register

  \param[in] xevtyper  The Performance Monitor Event Type Select Register
                       value
  \param[in] u         The value of the privileged execution filtering
                       bit
                          -0 Count events when executing at PL1.
                          -1 Do not count events when executing at PL1.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_xevtyper_set_p (unsigned int xevtyper,
                                               unsigned int        p)
{
    xevtyper = pmu_insert (xevtyper, p, PMU_XEVTYPER_V_P,
                                        PMU_XEVTYPER_M_P);
    return xevtyper;
}
/* ---------------------------------------------------------------------- */




/* ---------------------------------------------------------------------- *//*!

  \brief  Sets the value of the Performance Monitor Event Type Register
          privileged and unprivileged execution filtering bits.
  \return The new value of the Performance Monitor Event Type Select 
          Register

  \param[in] xevtyper  The Performance Monitor Event Type Select Register
                       value
  \param[in] pu        The value of the privileged execution filtering
                       bit
                          -0 Do count events when executing at PL0 or PL1.
                          -1 Do not count events when executing at PL0.
                          -2 Do not count events when executing at PL1.
                          -3 Do not count events when executing at PL0 or
                             PL1.
                                                                          */
/* ---------------------------------------------------------------------- */
static inline unsigned int pmu_xevtyper_set_pu  (unsigned int xevtyper,
                                                 unsigned int       pu)
{
    xevtyper = pmu_insert (xevtyper, pu, PMU_XEVTYPER_V_PU,
                                         PMU_XEVTYPER_M_PU);
    return xevtyper;
}
/* ---------------------------------------------------------------------- */


#ifdef __cplusplus
}
#endif


#endif

import React from 'react'
import { assets } from '../assets/assets'
import {ArrowRight, CalendarIcon,ClockIcon} from 'lucide-react'
import backgroundImage from '../assets/squid.jpg' 
import { useNavigate } from 'react-router-dom' 

const HeroSection = () => {
    const navigate=useNavigate()
  return (
    <div
    className='flex flex-col items-start justify-center gap-4 px-6 md:px-16 lg:px-36 bg-cover bg-center h-screen'
    style={{ backgroundImage: `url(${backgroundImage})` }}>
    
    <img src={assets.NetflixLogo2} className="max-h-20 lg:h-33 mt-20"/>
    <h1 className="text-5xl md:text-[70px] md:leading-18 font-semibold max-w-110">Squid Game 3</h1>
    <div className='flex items-center gap-4 text-gray-300'>
<span>Action | Survival </span>
<div className='flex items-center gap-1'>
        <CalendarIcon className='w-4.5 h-4.5'/>2025
</div>
<div className='flex items-center gap-1'>
        <ClockIcon className='w-4.5 h-4.5'/>2h 8m
        </div>
    </div>   
    <p className='max-w-md text-gray-300'>Hundreds of cash-strapped contestants accept an invitation 
        to compete in children's games for a tempting prize, but the stakes are deadly.</p>

        <button onClick={()=> navigate('/Series')} className='flex items-center gap-1 px-6 py-3 text-sm bg-primary
         hover:bg-primary-dull transition rounded-full font-medium cursor-pointer'>
             Explore Movies 
         <ArrowRight className='w-5 h-5'/>
         </button>
</div>

  )
}

export default HeroSection
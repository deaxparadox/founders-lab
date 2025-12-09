import HomeFilledIcon from '@mui/icons-material/HomeFilled';
import PortraitIcon from '@mui/icons-material/Portrait';
import RocketLaunchOutlinedIcon from '@mui/icons-material/RocketLaunchOutlined';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import AddCallIcon from '@mui/icons-material/AddCall';
import HelpOutlineOutlinedIcon from '@mui/icons-material/HelpOutlineOutlined';
import Groups2Icon from '@mui/icons-material/Groups2';
import MessageIcon from '@mui/icons-material/Message';
import ChecklistIcon from '@mui/icons-material/Checklist';
import GroupAddOutlinedIcon from '@mui/icons-material/GroupAddOutlined';
import WorkOutlineOutlinedIcon from '@mui/icons-material/WorkOutlineOutlined';
import EventOutlinedIcon from '@mui/icons-material/EventOutlined';
import InsertInvitationIcon from '@mui/icons-material/InsertInvitation';
import ContactEmergencyOutlinedIcon from '@mui/icons-material/ContactEmergencyOutlined';
import MonetizationOnOutlinedIcon from '@mui/icons-material/MonetizationOnOutlined';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authService, EXTERNAL_DASHBOARD_URL } from '../services/authService';
import { tokenStorage } from '../utils/tokenStorage';

export const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const activeTab = location.pathname.replace(/^\//, '') || 'ai-co-founder';
  const [isOpen, setIsOpen] = useState(false);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const handleKeyActivate = (fn) => (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fn();
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: HomeFilledIcon },
    { id: '7-step-roadmap', label: '7 Step Roadmap', icon: RocketLaunchOutlinedIcon },
    { id: 'education-hub', label: 'Education Hub', icon: AutoGraphIcon },
    { id: 'ai-co-founder', label: 'AI Co-founder', icon: PortraitIcon }, 
    { id: 'ai-assistant', label: 'AI Assistant', icon: HelpOutlineOutlinedIcon }, 
    { id: 'founder-support-directory', label: 'Founder Support Directory', icon: ContactEmergencyOutlinedIcon }, 
    { id: 'events', label: 'Events', icon: EventOutlinedIcon }, 
    { id: 'consult-expert', label: 'Consult Expert', icon: AddCallIcon },
    { id: 'hire-freelancer', label: 'Hire Freelancer', icon: Groups2Icon },
    { id: 'messages', label: 'Messages', icon: MessageIcon },
    { id: 'orders', label: 'Orders', icon: ChecklistIcon },
    { id: 'investor-connect', label: 'Investor Connect', icon: MonetizationOnOutlinedIcon },
    { id: 'co-founder-connect', label: 'Co-Founder Connect', icon: GroupAddOutlinedIcon },
    { id: 'post-job-internship', label: 'Post Job/Internship', icon: WorkOutlineOutlinedIcon },
    { id: 'account-settings', label: 'Account Settings', icon: SettingsIcon },
    { id: 'logout', label: 'Log out', icon: LogoutIcon },
  ];

  const renderButtons = () =>
    tabs.map((tab, index) => {
      const Icon = tab.icon;
      const handleClick = () => {
        // Close sidebar on mobile when a tab is clicked
        if (window.innerWidth < 768) {
          setIsOpen(false);
        }
        
        if (tab.id === 'ai-co-founder') {
          navigate(`/${tab.id}`);
        } else if (tab.id === 'ai-assistant') {
          const currentSid = tokenStorage.getSid();
          let externalUrl = `${EXTERNAL_DASHBOARD_URL}/entrepreneur/l24xh?tab=ai`;
          if (currentSid) {
            externalUrl += `&sid=${encodeURIComponent(currentSid)}`;
          }
          window.location.href = externalUrl;
        } else if (tab.id === 'logout') {
          authService.logout();
        } else {
          const tabMap = {
            overview: 'overview',
            '7-step-roadmap': '7-step',
            'education-hub': 'education',
            'consult-expert': 'expert',
            'hire-freelancer': 'freelancers',
            messages: 'messages',
            orders: 'orders',
            'founder-support-directory': 'directory',
            community: 'community',
            events: 'events',
            'account-settings': 'settings',
            'investor-connect': 'investor',
            'co-founder-connect': 'connect',
            'post-job-internship': 'jobs',
          };
          
          const currentSid = tokenStorage.getSid();
          const tabParam = tabMap[tab.id];
          
          let externalUrl = `${EXTERNAL_DASHBOARD_URL}?tab=${tabParam}`;
          if (currentSid) {
            externalUrl += `&sid=${encodeURIComponent(currentSid)}`;
          }
          
          window.location.href = externalUrl;
        }
      };

      // Add toggle button before Overview tab (first tab)
      if (index === 0) {
        return (
          <div key="toggle-wrapper" className="flex flex-col gap-2">
            
            
            {/* Overview Tab */}
            <div
              key={tab.id}
              className={`flex flex-row items-center justify-start gap-2 rounded-xl py-[5px] px-[29px] pr-8 cursor-pointer min-h-[48px] h-auto w-auto flex-shrink-0 ${
                activeTab === tab.id 
                  ? 'bg-[#27368F] text-white' 
                  : 'bg-transparent text-[#333333] hover:bg-black/[0.04]'
              }`}
              onClick={handleClick}
              onKeyDown={handleKeyActivate(() => handleClick())}
              role="button"
              tabIndex={0}
            >
              <div className="flex items-center justify-center min-w-[20px] max-w-[20px] w-5 min-h-[20px] max-h-[20px] h-5 flex-grow">
                <Icon sx={{ fontSize: 20 }} />
              </div>
              <div className="whitespace-pre-wrap text-[15px] font-normal leading-[1.6] w-max flex-grow-0 font-inter">
                {tab.label}
              </div>
            </div>
          </div>
        );
      }

      return (
        <div
          key={tab.id}
          className={`flex flex-row items-center justify-start gap-2 rounded-xl py-[5px] px-[29px] pr-8 cursor-pointer min-h-[48px] h-auto w-auto flex-shrink-0 ${
            activeTab === tab.id 
              ? 'bg-[#27368F] text-white' 
              : 'bg-transparent text-[#333333] hover:bg-black/[0.04]'
          }`}
          onClick={handleClick}
          onKeyDown={handleKeyActivate(() => handleClick())}
          role="button"
          tabIndex={0}
        >
          <div className="flex items-center justify-center min-w-[20px] max-w-[20px] w-5 min-h-[20px] max-h-[20px] h-5 flex-grow">
            <Icon sx={{ fontSize: 20 }} />
          </div>
          <div className="whitespace-pre-wrap text-[15px] font-normal leading-[1.6] w-max flex-grow-0 font-inter">
            {tab.label}
          </div>
        </div>
      );
    });

  return (
    <>
      {/* Floating Toggle Button - Always visible on small screens */}
      <button
        onClick={toggleSidebar}
        className="md:hidden fixed top-4 left-2 z-[70] text-white p-3 rounded-lg hover:bg-[#1e2a6f] transition-colors"
        aria-label="Toggle sidebar"
      >
        {isOpen ? (
  <CloseIcon sx={{ fontSize: 24, color: "#FFFFFF" }} />
) : (
  <MenuIcon sx={{ fontSize: 24, color: "#FFFFFF" }} />
)}

      </button>

      {/* Overlay for mobile when sidebar is open */}
      {isOpen && (
        <div
          className="fixed inset-0 z-[65] md:hidden "
          onClick={toggleSidebar}
          aria-hidden="true"
        />
      )}
      
      {/* Sidebar */}
      <div
        className={`fixed md:static top-[86px] md:top-0 left-0 z-[70] flex flex-col bg-[#F4F7FA] overflow-auto border-r border-solid border-[#e0e0e0] p-4 h-[calc(100vh-60px)] md:h-full transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 w-[327px] min-w-0`}
      >
        <div className="flex flex-col justify-start gap-2 min-w-[40px] w-full">
          {renderButtons()}
        </div>
      </div>
    </>
  );
};

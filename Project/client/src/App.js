import React, { useState, useEffect } from 'react';
import { Layout, theme } from 'antd';
import axios from 'axios';

import EventSetting from './components/Event/EventSetting';
import Events from './components/Event/Events';


const { Sider, Content } = Layout;

const App = () => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const [selectedEvent, setSelectedEvent] = useState({});
  const [events, setEvents] = useState([]);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const response = await axios.get('/events');
      setEvents(response.data);
      console.log(response.data)
    } catch (error) {
      console.error('Error fetching events:', error);
    }
  };

  const createEvent = async (values) => {
    await axios.post('/events', values);
  }

  const handleEventSelect = (event) => {
    setSelectedEvent(event);
    fetchEvents();
  }

  const handleEventDelete = () => {
    setSelectedEvent({});
    fetchEvents();
  }

  const handleEventChange = () => {
    fetchEvents();
  }

  const handleEventCreate = async (values) => {
    await createEvent(values);
    fetchEvents();
  }

  return (
    <Layout style={{minWidth: 800}}>

      <Sider trigger={null} theme='light' style={{
        overflow: 'auto',
        width: 600,
      }}
      >
        <Events events={events} onSelectEvent={handleEventSelect} onCreateEvent={handleEventCreate} />
      </Sider>
      <Layout>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 640,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          <EventSetting event={selectedEvent} onDeleteEvent={handleEventDelete} onChangeEvent={handleEventChange}></EventSetting>
        </Content>
      </Layout>
    </Layout>
  );
};

export default App;
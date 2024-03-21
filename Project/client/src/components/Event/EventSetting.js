import React, { useState, useEffect } from "react";
import { Button, DatePicker, Switch, message, Empty, Popconfirm, Flex, Space, Input, Typography, Modal, Table } from "antd";
import dayjs from 'dayjs';
import axios from 'axios';
import exportToExcel from '../Scripts/Excel';
import { Content } from "antd/es/layout/layout";
import Questions from "./Questions";

function toIsoString(date) {
  var tzo = -date.getTimezoneOffset(),
    dif = tzo >= 0 ? '+' : '-',
    pad = function (num) {
      return (num < 10 ? '0' : '') + num;
    };

  return date.getFullYear() +
    '-' + pad(date.getMonth() + 1) +
    '-' + pad(date.getDate()) +
    'T' + pad(date.getHours()) +
    ':' + pad(date.getMinutes()) +
    ':' + pad(date.getSeconds()) +
    dif + pad(Math.floor(Math.abs(tzo) / 60)) +
    ':' + pad(Math.abs(tzo) % 60);
}

const EventSetting = ({ event, onDeleteEvent, onChangeEvent }) => {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState(event.name);
  const [checkDate, setCheckDate] = useState(dayjs(event.check_date));
  const [maxBookings, setMaxBookings] = useState(event.max_bookings);
  const [closeDate, setCloseDate] = useState(dayjs(event.close_date));
  const [active, setActive] = useState(event.active);
  const [eventQuestions, setEventQuestions] = useState(event.data_type);

  const [eventBookingsData, setEventBookingsData] = useState([]);
  const [columnsBookingsData, setColumnsBookingsData] = useState([]);

  useEffect(() => {
    setName(event.name);
    setCheckDate(dayjs(event.check_date));
    setMaxBookings(event.max_bookings);
    setCloseDate(dayjs(event.close_date));
    setActive(event.active);
    setEventQuestions(event.data_type);
    handleGetBookings();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [event]);

  const handleSave = async () => {
    try {
      const updatedEvent = {
        ...event,
        name: name,
        check_date: toIsoString(checkDate.toDate()),
        max_bookings: maxBookings,
        data_type: eventQuestions,
        close_date: toIsoString(closeDate.toDate()),
        active: active
      };
      if (eventQuestions.length < 1) throw new Error("Отсутсвуют вопросы");
      console.log(updatedEvent)
      await axios.put(`/events/${event.id}`, updatedEvent);
      message.success('Мероприятие обновлено');
      onChangeEvent();
    } catch (error) {
      console.error('Ошибка обновления мероприятия:', error);
      message.error('Ошибка обновления мероприятия');
    }
  };
  
  const handleDelete = async () => {
    try {
      await axios.delete(`/events/${event.id}`);
      message.success('Мероприятие удалено');
      onDeleteEvent();
    } catch (error) {
      console.error('Ошибка удаления мероприятия:', error);
      message.error('Ошибка удаления мероприятия');
    }
  };

  const showModal = () => {
    setOpen(true);
    handleGetBookings();
  };

  const handleGetBookings = async () => {
    try {
      if (!event.id) return
      const response_event = await axios.get(`/events/${event.id}`);
      const response_bookings = await axios.get(`/events/${event.id}/bookings`);

      const columns = response_event.data.data_type.map((item, i) => ({
        title: item['question'],
        dataIndex: i,
        key: i
      }));

      const dataSource = response_bookings.data.map((item, i) => ({
        key: i,
        ...item['data']
      }))
      
      setEventBookingsData(dataSource);
      setColumnsBookingsData(columns);
    } catch (error) {
      console.error('Ошибка чтения броней:', error);
      // message.error('Ошибка чтения броней');
    }
  };

  const handleMaxBookingChange = (e) => {
    const value = e.target.value;
    const regex = /^\d*$/;
    if (!regex.test(value)) {
      e.target.value = value.slice(0, -1);
    }
    setMaxBookings(+e.target.value);
    handleGetBookings();
  };

  const handleDownloadExcel = () => {
    exportToExcel(eventBookingsData, columnsBookingsData.map(i => i.title), event.name);
    setOpen(false);
  };

  const handleCancel = () => {
    setOpen(false);
  };

  const handleQuestionChange = (questions) => {
    setEventQuestions(questions);
  };

  if (!event.id) return (<Empty description={"Выберите мероприятие"} />)

  return (
    <div>
      {event && (
        <Content>
          <Modal style={{ top: 0 }} width={'100%'} open={open} onOk={handleDownloadExcel} okText="Скачать Excel" onCancel={handleCancel}>
            <Table columns={columnsBookingsData} dataSource={eventBookingsData} />
          </Modal>
          <div>Id: {event.id}</div>
          <Flex vertical gap="small">
            <Flex gap="small" justify="space-between">
              <div  style={{ width: "60%" }}>
                <Typography.Title level={5}>Название мероприятия</Typography.Title>
                <Input type="text" value={name} onChange={value => setName(value.target.value)} maxLength={100}/>
              </div>
              <Space>
                <Button onClick={showModal}>Брони {eventBookingsData.length}</Button>
                <Button type="primary" onClick={handleSave}>Сохранить</Button>
                <Popconfirm
                  title="Удалить мероприятие?"
                  onConfirm={handleDelete}
                  okText="Да"
                  cancelText="Нет"
                >
                  <Button type="primary" danger>Удалить</Button>
                </Popconfirm>
              </Space>
            </Flex>

            <Flex gap="small">
              <div>
                <Typography.Title level={5}>Дата закрытия</Typography.Title>
                <DatePicker
                  showTime
                  value={closeDate}
                  onChange={value => setCloseDate(value)}
                />
              </div>
              <div>
                <Typography.Title level={5}>Дата проверки</Typography.Title>
                <DatePicker
                  showTime
                  value={checkDate}
                  onChange={value => setCheckDate(value)}
                />
              </div>
              <div>
                <Typography.Title level={5}>Ограничение</Typography.Title>
                <Input type="text" value={maxBookings} onChange={handleMaxBookingChange} maxLength={5}/>
              </div>
              <div>
                <Typography.Title level={5}>Активно</Typography.Title>
                <Switch
                  checked={active}
                  onChange={checked => setActive(checked)}
                />
              </div>
            </Flex>

          </Flex>
          <div style={{ marginTop: 20 }}>
            <Typography.Title level={3}>Вопросы</Typography.Title>
            <Questions eventQuestions={eventQuestions || []} onChange={handleQuestionChange}></Questions>
          </div>

        </Content>
      )}
    </div>
  );
};

export default EventSetting;

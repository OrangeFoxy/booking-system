import React, { useState } from 'react';
import { Input, Table, Button, Modal, Form, Layout } from 'antd';

const { Search } = Input;

const Events = ({ events, onSelectEvent, onCreateEvent }) => {
  const [searchText, setSearchText] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();


  const handleEventSelect = (event) => onSelectEvent(event);
  const handleSearch = (value) => setSearchText(value);
  const showModal = () => setIsModalVisible(true);
  const handleCancel = () => setIsModalVisible(false);

  const handleOk = () => {
    form
      .validateFields()
      .then(async (values) => {
        form.resetFields();
        setIsModalVisible(false);
        try {
          onCreateEvent(values);
        } catch (error) {
          console.error('Ошибка создания мероприятия:', error);
        }
      })
      .catch((info) => {
        console.log('Ошибки в проверке:', info);
      });
  };

  const filteredEvents = events.filter(event =>
    event.name.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns = [{ dataIndex: 'name', }];

  return (
    <Layout>
      <Search
        placeholder="Поиск"
        allowClear
        onSearch={handleSearch}
        style={{ padding: 8 }}
      />

      <Button type="primary" onClick={showModal}>Добавить</Button>

      <Modal title="Добавление мероприятия" open={isModalVisible} onOk={handleOk} onCancel={handleCancel} okText="Добавить" cancelText="Отмена">
        <Form form={form} name="addEventForm" initialValues={{}} layout="vertical">
          <Form.Item name="name" label="Название мероприятия" rules={[{ required: true, message: 'Введите название' }]}>
            <Input />
          </Form.Item>
          {/* Добавить другие поля для ввода данных мероприятия */}
        </Form>
      </Modal>
      <Table
        dataSource={filteredEvents}
        tableLayout='fixed'
        rowKey="id"
        showHeader={false}
        columns={columns}
        size="large"
        style={{ padding: 8 }}
        onRow={(record, rowIndex) => ({
          onClick: () => { handleEventSelect(record); console.log(record) },
        })}
      />
    </Layout>
  );
};

export default Events;

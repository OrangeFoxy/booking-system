import { DownOutlined } from '@ant-design/icons';
import { Button, Input, Form, Space, Dropdown, Flex } from 'antd';

const Questions = ({ eventQuestions, onChange }) => {

    const handleAddTextQuestion = () => {
        eventQuestions = [...eventQuestions, { type: 'text', question: '', mask: '' }];
        onChange(eventQuestions);
    };

    const handleAddOptionQuestion = () => {
        eventQuestions = [...eventQuestions, { type: 'option', question: '', options: [] }];
        onChange(eventQuestions);
    };

    const handleDeleteQuestion = (index) => {
        eventQuestions.splice(index, 1);
        onChange([...eventQuestions]);
    };

    const handleQuestionTextChange = (index, field, value) => {
        eventQuestions[index][field] = value;
        onChange([...eventQuestions]);
    };

    const handleOptionChange = (index, optionIndex, value) => {
        eventQuestions[index].options[optionIndex] = value;
        onChange([...eventQuestions]);
    };

    const handleAddOption = (index) => {
        eventQuestions[index].options.push('');
        onChange([...eventQuestions]);
    };

    const handleDeleteOption = (index, optionIndex) => {
        eventQuestions[index].options.splice(optionIndex, 1);
        onChange([...eventQuestions]);
    };

    const items = [
        {
            label: 'Текстовый вопрос',
            key: '1',
            onClick: handleAddTextQuestion
        },
        {
            label: 'Вопрос с выбором',
            key: '2',
            onClick: handleAddOptionQuestion
        }
    ];

    const renderTextQuestion = (question, index) => {
        return (
            <Flex key={index} style={{ marginBottom: 16 }} vertical>
                <Form.Item label={`Текстовый вопрос ${index + 1}`}>
                    <Input placeholder="Введите вопрос" value={question.question}
                        onChange={(event) => handleQuestionTextChange(index, 'question', event.target.value)} />
                </Form.Item>
                <Form.Item label="Шаблон">
                    <Input placeholder="Введите маску" value={question.mask}
                        onChange={(event) => handleQuestionTextChange(index, 'mask', event.target.value)} />
                </Form.Item>
                <Button type="primary" danger onClick={() => handleDeleteQuestion(index)}>Удалить вопрос</Button>
            </Flex>
        );
    };

    const renderOptionQuestion = (question, index) => {
        return (
            <Flex key={index} style={{ marginBottom: 16 }} vertical  gap={"small"}>
                <Form.Item label={`Вопрос с выбором ${index + 1}`}>
                    <Input placeholder="Введите вопрос" value={question.question}
                        onChange={(event) => handleQuestionTextChange(index, 'question', event.target.value)} />
                </Form.Item>
                <Button type="dashed" onClick={() => handleAddOption(index)}>Добавить вариант ответа</Button>
                <Flex  gap={"small"} justify="space-around" vertical>
                    {question.options.map((option, optionIndex) => (
                        <Flex key={optionIndex} style={{ marginBottom: 8, minWidth: 400 }} vertical  gap={"small"}>
                            <Input placeholder="Вариант ответа" value={option}
                                onChange={(event) => handleOptionChange(index, optionIndex, event.target.value)} />
                            <Button danger onClick={() => handleDeleteOption(index, optionIndex)}>Удалить вариант</Button>
                        </Flex>
                    ))}
                </Flex>
                <Button type="primary" danger onClick={() => handleDeleteQuestion(index)}>Удалить вопрос</Button>
            </Flex>
        );
    };

    return (
        <Flex vertical>
            <Flex justify="flex-start" align="flex-start">
                <Dropdown menu={{ items }}>
                    <Button>
                        <Space>Добавить<DownOutlined /></Space>
                    </Button>
                </Dropdown>
            </Flex>
            <Flex gap={"large"} style={{ minWidth: "70%", maxWidth: "70%"}}>
                <Form>
                    {eventQuestions.map((question, index) => {
                        if (question.type === 'text') {
                            return renderTextQuestion(question, index);
                        } else if (question.type === 'option') {
                            return renderOptionQuestion(question, index);
                        }
                        return null;
                    })}
                </Form>
            </Flex>
        </Flex>
    );
};

export default Questions;

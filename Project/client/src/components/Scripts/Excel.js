import * as XLSX from 'xlsx';

const exportToExcel = (data, columns, filename) => {
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');

    const headerRow = columns.map(column => ({
        value: column.title,
        font: { bold: true }
    }));
    XLSX.utils.sheet_add_aoa(worksheet, [headerRow], { origin: 'A1' });

    columns.forEach((column, index) => {
        worksheet['!cols'] = [{ wch: column.width || 20 }];
    });

    XLSX.writeFile(workbook, `${filename}.xlsx`);
};

export default exportToExcel;
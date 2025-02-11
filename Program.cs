using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using CsvHelper;
using HtmlAgilityPack;

namespace LotteryDataCrawler
{
    class Program
    {
        static async Task Main(string[] args)
        {
            // 目标 URL
            string url = "https://datachart.500.com/ssq/history/newinc/history.php?start=1&end=25013";

            // 获取并解析数据
            var data = await ParseLotteryData(url);

            // 保存数据到 CSV
            string csvFilePath = Path.Combine(Environment.CurrentDirectory, "ssq_data.csv");
            using (var writer = new StreamWriter(csvFilePath))
            using (var csv = new CsvWriter(writer, System.Globalization.CultureInfo.InvariantCulture))
            {
                csv.WriteRecords(data);
            }

            Console.WriteLine($"数据已保存到：{csvFilePath}");
        }

        static async Task<List<LotteryData>> ParseLotteryData(string url)
        {
            var data = new List<LotteryData>();

            using (var client = new HttpClient())
            {
                // 获取 HTML 内容
                var response = await client.GetStringAsync(url);
                var doc = new HtmlDocument();
                doc.LoadHtml(response);

                // 解析表格行
                var rows = doc.DocumentNode.SelectNodes("//tbody[@id='tdata']//tr[@class='t_tr1']");
                if (rows == null)
                {
                    Console.WriteLine("未找到数据行，请检查 HTML 结构！");
                    return data;
                }

                foreach (var row in rows)
                {
                    var cells = row.SelectNodes("td");
                    if (cells == null || cells.Count < 8) continue; // 确保有足够的列

                    var item = new LotteryData
                    {
                        IssueNumber = cells[0].InnerText.Trim(), // 期号
                        RedBalls = new List<string>
                        {
                            cells[1].InnerText.Trim(), // 红球 1
                            cells[2].InnerText.Trim(), // 红球 2
                            cells[3].InnerText.Trim(), // 红球 3
                            cells[4].InnerText.Trim(), // 红球 4
                            cells[5].InnerText.Trim(), // 红球 5
                            cells[6].InnerText.Trim()  // 红球 6
                        },
                        BlueBall = cells[7].InnerText.Trim() // 蓝球
                    };

                    data.Add(item);
                }
            }

            return data;
        }
    }

    class LotteryData
    {
        public string IssueNumber { get; set; } // 期号
        public List<string> RedBalls { get; set; } // 红球
        public string BlueBall { get; set; } // 蓝球
    }
}
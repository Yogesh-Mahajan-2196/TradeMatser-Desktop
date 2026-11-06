document.addEventListener("alpine:init", () => {
  Alpine.data("purchaseSellGraph", () => {
    let chartInstance = null;

    return {
      period: "1month",
      loading: false,
      error: "",

      init() {
        this.$nextTick(() => {
          this.createChart();
          this.loadGraphData();
        });
      },

      createChart() {
        const canvas = this.$refs.chart;
        if (!canvas) {
          console.error("Graph canvas not found");
          return;
        }

        const existingChart = Chart.getChart(canvas);
        if (existingChart) existingChart.destroy();

        chartInstance = new Chart(canvas, {
          type: "bar",
          data: {
            labels: [],
            datasets: [
              { label: "Purchase", data: [], backgroundColor: "#16a34a", borderRadius: 6 },
              { label: "Sell", data: [], backgroundColor: "#2563eb", borderRadius: 6 },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "top" } },
            scales: {
              y: { beginAtZero: true, ticks: { maxTicksLimit: 6 } },
              x: { grid: { display: false } },
            },
          },
        });
      },

      async loadGraphData() {
        this.loading = true;
        this.error = "";

        try {
          const url = `/purchase-vs-sell?period=${this.period}`;
          const response = await fetch(url);

          if (!response.ok) {
            const responseText = await response.text();
            console.error("API response:", responseText);
            throw new Error(`API error: ${response.status}`);
          }

          const graphData = await response.json();

          if (!chartInstance) this.createChart();

          chartInstance.data.labels = graphData.labels;
          chartInstance.data.datasets[0].data = graphData.purchase;
          chartInstance.data.datasets[1].data = graphData.sell;
          chartInstance.update();
        } catch (error) {
          console.error("Graph error:", error);
          this.error = error.message;
        } finally {
          this.loading = false;
        }
      },

      destroy() {
        if (chartInstance) {
          chartInstance.destroy();
          chartInstance = null;
        }
      },
    };
  });
});

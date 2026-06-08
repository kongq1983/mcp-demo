export const leaveService = {
  async submitLeave(leaveForm) {
    try {
      const response = await fetch('http://localhost:8001/leave/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(leaveForm),
      });
      return await response.json();
    } catch (error) {
      throw error;
    }
  }
};

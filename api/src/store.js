const { v4: uuidv4 } = require('uuid');

let store = {
  users: new Map(),
  items: new Map(),
};

function resetStore() {
  store.users = new Map();
  store.items = new Map();
}

module.exports = { store, resetStore };

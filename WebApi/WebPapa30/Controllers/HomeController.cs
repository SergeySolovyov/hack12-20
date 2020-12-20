using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using WebPapa30.ViewModels;

namespace WebPapa30.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class HomeController : ControllerBase
    {
        // GET: HomeController
        [Route("customers")]
        public ActionResult GetCustomers()
        {
            using (AppContext db = new AppContext())
            {
                var customers = db.Customers.ToList();

                return new JsonResult(customers);
            }
        }

        // GET: HomeController
        [Route("tenders")]
        public ActionResult GetTenders()
        {
            using (AppContext db = new AppContext())
            {
                var tenders = db.Tenders.Include(t => t.Winner).ToList();

                return new JsonResult(tenders);
            }
        }

        // GET: HomeController
        [Route("participants")]
        public ActionResult GetPatricipants()
        {
            using (AppContext db = new AppContext())
            {
                var winners = db.Winners.GroupBy(w => w.INN).ToList();

                var participantViewModel = winners.Select(w => new ParticipantViewModel
                {
                    Winner = w.FirstOrDefault(),
                    WinCount = w.Count()
                });

                return new JsonResult(participantViewModel);
            }
        }
    }
}

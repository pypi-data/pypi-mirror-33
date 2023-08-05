from datmo.core.util.validation import validate
from datmo.core.util.i18n import get as __
from datmo.core.controller.base import BaseController
from datmo.core.entity.model import Model
from datmo.core.entity.session import Session
from datmo.core.util.exceptions import (ProjectNotInitialized,
                                        EnvironmentInitFailed, FileIOError)


class ProjectController(BaseController):
    """ProjectController inherits from BaseController and manages business logic related to the
    project. One model is associated with each project currently.

    Parameters
    ----------
    home : str
        home path of the project

    Methods
    -------
    init(name, description)
        Initialize the project repository as a new model or update the existing project
    cleanup()
        Remove all datmo references from the current repository. NOTE: THIS WILL DELETE ALL DATMO WORK
    status()
        Give the user a picture of the status of the project, snapshots, and tasks
    """

    def __init__(self):
        super(ProjectController, self).__init__()

    def init(self, name, description):
        """ Initialize the project

        This function will initialize the project or reinitialize it the project is
        already initialized.

        Parameters
        ----------
        name : str
        description : str

        Returns
        -------
        bool

        Raises
        ------
        SessionDoesNotExist
        """
        # Create the Model, is it new or update?
        is_new_model = False
        old_model = self.model
        if not self.model:
            is_new_model = True

        try:
            # Always validate inputs to the init function
            validate("create_project", {
                "name": name,
                "description": description
            })

            # Create model if new else update
            if is_new_model:
                _ = self.dal.model.create(
                    Model({
                        "name": name,
                        "description": description
                    }))
            else:
                self._model = self.dal.model.update({
                    "id": self.model.id,
                    "name": name,
                    "description": description
                })

            # Initialize Code Driver if needed
            if not self.code_driver.is_initialized:
                self.code_driver.init()

            # Initialize File Driver if needed
            if not self.file_driver.is_initialized:
                self.file_driver.init()

            # Initialize Environment Driver if needed
            # (not required but will warn if not present)
            try:
                if not self.environment_driver.is_initialized:
                    self.environment_driver.init()
            except EnvironmentInitFailed:
                self.logger.warning(
                    __("warn", "controller.general.environment.failed"))

            # Build the initial default Environment (NOT NECESSARY)
            # self.environment_driver.build_image(tag="datmo-" + \
            #                                  self.model.name)

            # Create and set current session
            if is_new_model:
                # Create new default session
                _ = self.dal.session.create(
                    Session({
                        "name": "default",
                        "model_id": self.model.id,
                        "current": True
                    }))
            else:
                if not self.current_session:
                    default_session_objs = self.dal.session.query({
                        "name": "default",
                        "model_id": self.model.id
                    })
                    if not default_session_objs:
                        # Creating a default session since none exists
                        _ = self.dal.session.create(
                            Session({
                                "name": "default",
                                "model_id": self.model.id,
                                "current": True
                            }))
                    else:
                        # Update default session to be current
                        default_session_obj = default_session_objs[0]
                        self.dal.session.update({
                            "id": default_session_obj.id,
                            "current": True
                        })
            return True
        except Exception:
            # if any error occurred with new model, ensure no initialize occurs and raise previous error
            # if any error occurred with existing model, ensure no updates were made, raise previous error
            if is_new_model:
                self.cleanup()
            else:
                self._model = self.dal.model.update({
                    "id": old_model.id,
                    "name": old_model.name,
                    "description": old_model.description
                })
            raise

    def cleanup(self):
        """Cleans the project structure completely

        Notes
        -----
        This function will not error out but will gracefully exit, since
        it is used in cases where init fails as a check against mid-initialized
        projects

        Returns
        -------
        bool
        """
        if not self.is_initialized:
            self.logger.warning(
                __("warn", "controller.project.cleanup.not_init"))
        # Remove Datmo environment_driver references, give warning if error
        try:
            # Obtain image id before cleaning up if exists
            images = self.environment_driver.list_images(name="datmo-" + \
                                                              self.model.name)
            image_id = images[0].id if images else None
        except Exception:
            self.logger.warning(
                __("warn", "controller.project.cleanup.environment"))

        # Remove Datmo code_driver references, give warning if error
        try:
            if self.code_driver.is_initialized:
                for ref in self.code_driver.list_refs():
                    self.code_driver.delete_ref(ref)
        except Exception:
            self.logger.warning(__("warn", "controller.project.cleanup.code"))

        # Remove Datmo file structure, give warning if error
        try:
            self.file_driver.delete_datmo_file_structure()
        except FileIOError:
            self.logger.warning(__("warn", "controller.project.cleanup.files"))

        try:
            if image_id:
                # Remove image created during init
                self.environment_driver.remove_image(
                    image_id_or_name=image_id, force=True)

                # Remove any dangling images (optional)

                # Stop and remove all running environments with image_id
                self.environment_driver.stop_remove_containers_by_term(
                    image_id, force=True)
        except Exception:
            self.logger.warning(
                __("warn", "controller.project.cleanup.environment"))

        return True

    def status(self):
        """Return the project status information if initialized

        Returns
        -------
        status_dict : dict
            dictionary with project metadata and config
        latest_snapshot : datmo.core.entity.snapshot.Snapshot
            snapshot object of the latest snapshot if present else None
        ascending_unstaged_tasks : list
            list of datmo.core.entity.task.Task objects in ascending order of updated_at time
        """
        if not self.is_initialized:
            raise ProjectNotInitialized(
                __("error", "controller.project.status"))
        # TODO: Add in note when environment is not setup or intialized

        # Add in project metadata
        status_dict = self.model.to_dictionary().copy()

        # Show all project settings
        status_dict["config"] = self.config_store.to_dict()

        # Show the latest visible snapshot
        descending_snapshots = self.dal.snapshot.query(
            {
                "visible": True
            }, sort_key="created_at", sort_order="descending")
        latest_snapshot = descending_snapshots[
            0] if descending_snapshots else None

        # Show unstaged tasks (created after latest snapshot)
        # TODO: use DB querying, currently returning randomly anomalous values for range queries
        # if latest_snapshot:
        #     task_query = {
        #         "updated_at": {
        #             "$gte":
        #                 latest_snapshot.created_at
        #                 .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        #         }
        #     }
        # else:
        #     task_query = {}

        descending_tasks = self.dal.task.query(
            {}, sort_key="updated_at", sort_order="descending")

        ascending_unstaged_tasks = []
        for task in descending_tasks:
            if task.updated_at >= latest_snapshot.created_at:
                ascending_unstaged_tasks.insert(0, task)
            else:
                break

        return status_dict, latest_snapshot, ascending_unstaged_tasks
